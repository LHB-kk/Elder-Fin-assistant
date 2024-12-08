import oss2
def gene_url(filename):
    try:
        auth = oss2.Auth('param1', 'param2')
        bucket = oss2.Bucket(auth, 'xxxx', 'xxxx')

        bucket.put_object_from_file(key=f'{filename}',filename=f'./pic/{filename}')

        url = bucket.sign_url('GET', f'{filename}',86400) 
    except Exception as e:
        print(f"{str(e)}")
