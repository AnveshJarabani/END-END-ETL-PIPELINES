import requests,json
def cost_extractor(i, raw, cookies):
    dict = json.loads(requests.get(raw.format(i), cookies=cookies).text)
    if not dict['PrceTiers']:
        # print(dict['PrceTxt'])
        return {'PN': [i],
                '$$': [dict['PrceTxt']],
                'T': None}
    else:
        dct=dict['PrceTiers']
        # print([(i['PrceTierPrceTxt'], i['PrceTierQtyTxt'])
            #    for i in dict['PrceTiers']])
        return {'PN': [i]*len(dct),
                '$$': [i['PrceTierPrceTxt']
                       for i in dct],
                'T': [i['PrceTierQtyTxt']
                      for i in dct]}
