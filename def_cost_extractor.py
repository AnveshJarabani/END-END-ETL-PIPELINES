import requests,json
def cost_extractor(i, raw, cookies):
    lnk = raw.format(i)
    dict = json.loads(requests.get(lnk, cookies=cookies).text)
    if not dict['PrceTiers']:
        # print(dict['PrceTxt'])
        data = {'PN': [i],
                '$$': [dict['PrceTxt']],
                'T': None}
    else:
        data = {'PN': [],
                '$$': [],
                'T': []}
        data['PN'].extend([i]*len(dict['PrceTiers']))
        data['$$'].extend([i['PrceTierPrceTxt']
                           for i in dict['PrceTiers']])
        data['T'].extend(i['PrceTierQtyTxt']
                         for i in dict['PrceTiers'])
        # print([(i['PrceTierPrceTxt'], i['PrceTierQtyTxt'])
            #    for i in dict['PrceTiers']])
    return data
