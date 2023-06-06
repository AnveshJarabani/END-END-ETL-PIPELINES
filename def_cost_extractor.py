import requests,json
def cost_extractor(i, raw, cookies):
    lnk = raw.format(i)
    dict = json.loads(requests.get(lnk, cookies=cookies).text)
    if not dict['PrceTiers']:
        # print(dict['PrceTxt'])
        return {'PN': [i],
                '$$': [dict['PrceTxt']],
                'T': None}
    else:
        return {'PN': [i]*len(dict['PrceTiers']),
                '$$': [i['PrceTierPrceTxt']
                       for i in dict['PrceTiers']],
                'T': [i['PrceTierQtyTxt']
                      for i in dict['PrceTiers']]}
        # print([(i['PrceTierPrceTxt'], i['PrceTierQtyTxt'])
            #    for i in dict['PrceTiers']])
