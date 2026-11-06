"""Vietnamese workflow presentation. Never changes executable inputs or links."""
import copy

NAMES={1:'Nâng cao · Model H3 Ref2V',2:'Nâng cao · Encoder native — không cần mmproj',
3:'Nâng cao · VAE hình ảnh',4:'Nâng cao · VAE âm thanh',
5:'01 · STORYBOARD — nguyên trang',6:'02 · NHÂN VẬT 1 — Picture 2',
7:'02 · NHÂN VẬT 2 — Picture 3',8:'02 · NHÂN VẬT 3 — Picture 4',
9:'03 · THỜI LƯỢNG CLIP (GIÂY)',10:'04 · PROMPT VIDEO & THAM CHIẾU',11:'Nâng cao · LoRA Turbo',
12:'Điều kiện tạo video',13:'04 · SEED — dùng lại để so sánh',14:'Thuật toán lấy mẫu',
15:'05 · CHẤT LƯỢNG — số bước',16:'06 · TẠO VIDEO',17:'Giải mã hình ảnh',
18:'Giải mã âm thanh',20:'07 · VIDEO GỐC — MP4',21:'Model tăng độ phân giải',
22:'08 · TĂNG ĐỘ PHÂN GIẢI 2×',24:'09 · VIDEO ĐÃ NÂNG — MP4'}
LABELS={'clip':'Bộ mã hóa','vae':'VAE hình ảnh','audio_vae':'VAE âm thanh','storyboard':'Storyboard · Picture 1',
'character_1':'Nhân vật 1 · Picture 2','character_2':'Nhân vật 2 · Picture 3','character_3':'Nhân vật 3 · Picture 4',
'seconds':'Thời lượng clip (giây)','prompt':'Prompt tiếng Anh','roles_json':'Ánh xạ ảnh (JSON)','width':'Chiều rộng','height':'Chiều cao',
'length':'Số khung hình','ref_image_size':'Mức chi tiết tham chiếu','images':'Khung hình',
'audio':'Âm thanh','fps':'FPS','crf':'Mức nén CRF','batch_size':'Số frame mỗi lượt','model':'Model',
'filename_prefix':'Thư mục / tên video','noise_seed':'Seed','steps':'Số bước','scheduler':'Lịch lấy mẫu',
'positive':'Điều kiện','av_latent':'Latent hình + âm','resolved_prompt':'Prompt đã khớp ảnh'}
POSITIONS={5:(40,260,340,500),6:(420,260,340,500),7:(40,810,340,500),8:(420,810,340,500),
9:(930,260,610,190),10:(930,530,610,830),13:(1710,260,480,160),14:(1710,470,480,110),12:(1710,630,480,140),
15:(1710,830,480,220),16:(1710,1110,480,200),
17:(2360,260,470,100),18:(2360,370,470,100),20:(2360,530,470,300),
21:(2910,260,470,100),22:(2910,430,470,210),24:(2910,740,470,300),
1:(40,1740,320,100),2:(420,1740,320,100),3:(800,1740,320,100),4:(1180,1740,320,100),11:(1560,1740,320,100)}


def beautify(workflow):
    w=copy.deepcopy(workflow)
    for n in w['nodes']:
        i=n['id'];n['title']=NAMES.get(i,n['type'])
        if i in POSITIONS:
            x,y,width,height=POSITIONS[i];n['pos']=[x,y];n['size']=[width,height]
        n['color']='#193845';n['bgcolor']='#142833'
        if i in [5,6,7,8]:n['color']='#245444';n['bgcolor']='#182f28'
        if i==10:n['color']='#334569';n['bgcolor']='#202c43'
        if i in [20,24]:n['color']='#635022';n['bgcolor']='#362e1e'
        if i in [1,2,3,4,11,17,18,21]:n.setdefault('flags',{})['collapsed']=True
        for port in n.get('inputs',[])+n.get('outputs',[]):port['label']=LABELS.get(port['name'],port['name'])
    maxid=max((n['id'] for n in w['nodes']),default=0)
    notes=[
      (0,-90,1540,220,'BẮT ĐẦU TẠI ĐÂY',
       '1. Chọn nguyên storyboard và đúng sheet nhân vật.  2. Kiểm tra Picture 1/2/3/4.\n'
       '3. Dán prompt tiếng Anh, chọn kích thước và số frame.  4. Bấm Thực thi / Queue.\n'
       'Lưới 2×2, 2×3, 3×3 đều dùng được. Chỉ ảnh đã nối mới được truyền cho model.\n'
       'Bản gốc và bản upscale lưu trong output/h3studio. Model/encoder nằm ở nhóm Nâng cao phía dưới.'),
      (1650,-90,1790,220,'MẸO CHẤT LƯỢNG',
       'match = nhẹ hơn; max = giữ tham chiếu lớn hơn, tốn VRAM hơn.\n'
       'Baseline 20 bước để kiểm tra; Turbo 4 bước là cấu hình so sánh, không chắc tốt hơn.\n'
       'Video 15 giây: 362 frame ở 24 FPS (~15,08 giây); cắt dựng về 15 giây khi cần.\n'
       'Nếu mặt sai hình hoặc đổi người, sửa ảnh/prompt trước upscale. Không cần đổi ngôn ngữ ComfyUI toàn hệ thống.')]
    for x,y,width,height,title,text in notes:
        maxid+=1;w['nodes'].append({'id':maxid,'type':'Note','title':title,'pos':[x,y],'size':[width,height],
          'flags':{},'order':len(w['nodes']),'mode':0,'properties':{},'widgets_values':[text],
          'color':'#343b49','bgcolor':'#202631'})
    specs=[('01–02 · ẢNH ĐẦU VÀO',0,200,800,1200,'#3b8f76'),
           ('03 · PROMPT & ĐÚNG NHÂN VẬT',890,200,690,1200,'#5877b6'),
           ('04–06 · THIẾT LẬP & TẠO VIDEO',1670,200,560,1200,'#438b9c'),
           ('07–09 · KẾT QUẢ & NÂNG CHẤT LƯỢNG',2320,200,1100,1200,'#a88a42'),
           ('NÂNG CAO · MODEL — KHÔNG CẦN SỬA KHI ĐÃ CÀI',0,1660,1950,260,'#646b7c')]
    w['groups']=[{'id':i+1,'title':t,'bounding':[x,y,ww,hh],'color':color,'font_size':24,'flags':{}} for i,(t,x,y,ww,hh,color) in enumerate(specs)]
    w['last_node_id']=maxid
    w.setdefault('extra',{})['ds']={'scale':0.45,'offset':[100,180]}
    w['extra']['h3studio_ui_version']='0.2.0-vi'
    return w
