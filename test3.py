sb = "/asdfasd/asdfasd/response/dd"
path_parts = sb.split('/') 
if len(path_parts) >= 2 and path_parts[-2] == 'response':
    print('true')