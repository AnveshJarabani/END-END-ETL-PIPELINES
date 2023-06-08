import requests
import json
import re
# from rich import print
def cost_extractor(i, raw, cookies):
    asp_lnk = 'https://www.mcmaster.com/WebParts/Content/ItmPrsnttnWebPart.aspx?partnbrtxt={}'.format(
        i)
    r = requests.get(asp_lnk, cookies=cookies).text
    ext = re.search(r'"ThumbnailSrc":"([^"]+)"', r).group(1)
    png_lnk = 'https://www.mcmaster.com/{}'.format(ext)
    dict = json.loads(requests.get(raw.format(i), cookies=cookies).text)
    if not dict['PrceTiers']:
        # print(dict['PrceTxt'])
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

