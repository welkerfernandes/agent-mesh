from fastapi import HTTPException
from .infrastructure import demo_metadata,digest

def execute_task(task,mode,api):
    if mode=='demo':
        payload={'weather':{'maximum_temperature_c':34,'rain_mm':12},
                 'economy':{'country':'BRA','year':2030,'gdp_per_capita_usd':12000},
                 'registry':{'cnpj':'00000000000191','status':'ATIVA'}}[task.tool]
        provenance=demo_metadata(payload)
    elif task.tool=='weather':
        raw,provenance=api.get('https://api.open-meteo.com/v1/forecast',{'latitude':-17.74,'longitude':-48.63,
               'daily':'temperature_2m_max,precipitation_sum','forecast_days':1,'timezone':'UTC'})
        try: payload={'date':raw['daily']['time'][0],'maximum_temperature_c':raw['daily']['temperature_2m_max'][0],'rain_mm':raw['daily']['precipitation_sum'][0]}
        except (KeyError,TypeError,IndexError): raise HTTPException(502,'Weather evidence schema rejected')
    elif task.tool=='economy':
        raw,provenance=api.get('https://api.worldbank.org/v2/country/BRA/indicator/NY.GDP.PCAP.CD',{'format':'json','per_page':10})
        try:
            row=next(r for r in raw[1] if r['value'] is not None)
            if row.get('countryiso3code')!='BRA': raise ValueError('Wrong country')
            payload={'country':'BRA','year':row['date'],'gdp_per_capita_usd':row['value']}
        except (KeyError,TypeError,IndexError,StopIteration,ValueError): raise HTTPException(502,'Economic evidence schema rejected')
    else:
        raw,provenance=api.get('https://brasilapi.com.br/api/cnpj/v1/00000000000191')
        try:
            if raw['cnpj']!='00000000000191':raise ValueError('Wrong entity')
            payload={'cnpj':raw['cnpj'],'status':raw['descricao_situacao_cadastral']}
        except (KeyError,TypeError,ValueError): raise HTTPException(502,'Registry evidence schema rejected')
    summary=task.tool+': '+str(payload)
    return {'id':task.id,'tool':task.tool,'question':task.question,'summary':summary,
            'payload':payload,'provenance':provenance,'content_sha256':digest(payload)}
