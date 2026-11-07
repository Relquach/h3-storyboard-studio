"""Optional reference chain, with stable original slot IDs and explicit bypass."""
import re
EMPTY_IMAGE='h3studio/disabled-reference.png'


def ensure_empty_image():
    import base64,pathlib,folder_paths
    path=pathlib.Path(folder_paths.get_input_directory())/EMPTY_IMAGE
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC'))
    return EMPTY_IMAGE


def resolve_extras(prompt, items, first_slot=2):
    active=[];mapping={};notes=[]
    for index,item in enumerate(items or []):
        old=first_slot+index
        if item.get('enabled') and item.get('image') is not None:
            mapping[old]=first_slot+len(active);active.append(item)
        else:
            mapping[old]=1
            notes.append(f'{item.get("name", "Reference "+str(index+1))}: external reference bypassed; use only what is visible in the storyboard for this asset.')
    # Single pass, so renumbering never rewrites a newly assigned Picture tag again.
    prompt=re.sub(r'<Picture (\d+)>',lambda m:f'<Picture {mapping.get(int(m.group(1)),int(m.group(1)))}>',prompt)
    if notes:prompt+='\n\nBYPASSED REFERENCES:\n'+'\n'.join(notes)
    return prompt,active


class H3StudioExtraReference:
    @classmethod
    def INPUT_TYPES(cls):
        import folder_paths
        import os
        empty=ensure_empty_image()
        root=folder_paths.get_input_directory()
        files=[]
        for directory,_,names in os.walk(root):
            for name in names:
                if name.lower().endswith(('.png','.jpg','.jpeg','.webp')):
                    files.append(os.path.relpath(os.path.join(directory,name),root))
        return {'required':{
            'enabled':('BOOLEAN',{'default':False}),
            'name':('STRING',{'default':'Tham chiếu bổ sung'}),
            'role':(['Nhân vật','Môi trường','Đạo cụ / vũ khí','Phong cách','Khác'],),
            'image':([empty]+sorted(set(files)-{empty}),{'image_upload':True}),
        },'optional':{'previous':('H3_EXTRA_REFS',)}}
    RETURN_TYPES=('H3_EXTRA_REFS',)
    RETURN_NAMES=('Danh sách tham chiếu',)
    FUNCTION='append'
    CATEGORY='H3 Storyboard Studio'

    def append(self,enabled,name,role,image,previous=None):
        items=list(previous or [])
        if len(items)>=8:raise ValueError('Tối đa 8 ô tham chiếu thêm, cộng storyboard là 9 ảnh.')
        tensor=None
        if enabled:
            if image in ('(Không dùng)',EMPTY_IMAGE):raise ValueError(f'{name}: chọn ảnh hoặc tắt Bật tham chiếu.')
            import nodes
            tensor=nodes.LoadImage().load_image(image)[0]
        english={'Nhân vật':'Character identity','Môi trường':'Environment','Đạo cụ / vũ khí':'Object / weapon','Phong cách':'Visual style','Khác':'Additional asset'}
        items.append({'enabled':bool(enabled),'name':name,'role':english.get(role,role),'image':tensor})
        return (items,)
