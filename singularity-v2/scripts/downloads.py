"""Resumable verified downloads. Does not replace existing mismatching files."""
import hashlib,pathlib,time,urllib.request

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def download(url, dest, expected_size=None, expected_hash=None, attempts=4):
    dest=pathlib.Path(dest); dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        if (expected_size is None or dest.stat().st_size==expected_size) and (not expected_hash or sha256(dest)==expected_hash):
            print('Verified existing:',dest.name,flush=True);return
        # Do not delete or replace an existing user's model on a mismatch.
        raise RuntimeError(f'Existing file differs from manifest: {dest}. Rename it manually before retrying.')
    part=dest.with_name(dest.name+'.part')
    for attempt in range(attempts):
        start=part.stat().st_size if part.exists() else 0
        if expected_size and start==expected_size:break
        try:
            req=urllib.request.Request(url,headers={'Range':f'bytes={start}-'} if start else {})
            with urllib.request.urlopen(req,timeout=60) as response:
                resumed=start>0 and response.status==206
                if resumed and not response.headers.get('Content-Range','').startswith(f'bytes {start}-'):
                    raise RuntimeError('Server returned a mismatched download range')
                mode='ab' if resumed else 'wb'
                with open(part,mode) as out:
                    copied=start if resumed else 0;last=time.monotonic()
                    while True:
                        data=response.read(4*1024*1024)
                        if not data:break
                        out.write(data);copied+=len(data)
                        if time.monotonic()-last>10:
                            print(f'{dest.name}: {copied/1e9:.2f} GB',flush=True);last=time.monotonic()
            break
        except Exception:
            if attempt+1==attempts:raise
            time.sleep(min(2**attempt,8))
    if expected_size is not None and part.stat().st_size!=expected_size:raise RuntimeError('Incomplete download: '+dest.name)
    if expected_hash and sha256(part)!=expected_hash:
        # Keep it for diagnosis, but do not repeatedly resume a corrupt full file.
        part.rename(part.with_name(part.name+'.corrupt-'+str(time.time_ns())))
        raise RuntimeError('SHA256 mismatch: '+dest.name)
    part.replace(dest)

