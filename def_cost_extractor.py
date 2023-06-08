import requests
import json
import re
def cost_extractor(i, raw, cookies):
    asp_lnk = 'https://www.mcmaster.com/WebParts/Content/ItmPrsnttnWebPart.aspx?partnbrtxt={}'.format(
        i)
    r = requests.get(asp_lnk, cookies=cookies).text
    ext = re.search(r'"ThumbnailSrc":"([^"]+)"', r).group(1)
    png_lnk = 'https://www.mcmaster.com/{}'.format(ext)
    dict = json.loads(requests.get(raw.format(i), cookies=cookies).text)
    local_path = r"C:\Users\ajarabani\Downloads\{}.png".format(i)
    with open(local_path,'wb') as f:
        f.write(requests.get(png_lnk).content)
    if not dict['PrceTiers']:
        return {'PN': [i],
                '$$': [dict['PrceTxt']],
                'T': [None],
                'png': [png_lnk]}
    else:
        dct = dict['PrceTiers']
        return {'PN': [i]*len(dct),
                '$$': [i['PrceTierPrceTxt']
                       for i in dct],
                'T': [i['PrceTierQtyTxt']
                      for i in dct],
                'png': [png_lnk]*len(dct)}
