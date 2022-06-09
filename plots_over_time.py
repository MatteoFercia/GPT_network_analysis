# ----------------------------------------------------------------------------------------------------------------------

from graph_details import get_results
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------------------------------------------------

def get_list_dwpi_codes(res):
    l = []
    for key, value in res.items():
        for k,v in res[key]['betweennes'].items():
            l.append(k)
    l = list(set(l))
    return l


def line_chart(res, dwpi_code, indicator, years, title, show=False):

    values = []
    for year in years:
        measure = res[year][indicator]
        if dwpi_code in measure.keys():
            for k, v in measure.items():
                if k==dwpi_code:
                    values.append((year,v))
        else:
            values.append((year, 0))

    x = list(map(lambda x: x[0], values))
    y = list(map(lambda x: x[1], values))
    x = np.array(x)
    y = np.array(y)

    plt.plot(x, y, marker='o')
    plt.title(title)
    if show: plt.show()

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    years = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020']
    results = get_results(years=years)
    print(results)

    indicators = [ 'clustering_coef' ] # 'betweennes', 'clustering_coef' ] # 'centrality'
    codes = get_list_dwpi_codes(res=results)

    # codes = ['W01-A','T01-S', 'T01-D'] # ['T01-D', 'T01-N', 'T01-F', 'T06-A', 'W01-A', 'W01-C', 'T01-S', 'T01-J']

    for indicator in indicators:
        for dwpi_code in codes:
            line_chart(res=results, dwpi_code=dwpi_code, years=years, indicator=indicator,
                       title=f'{indicator.title()} of {dwpi_code} over time', show=True)


            # if indicator == 'clustering_coef':
            #     line_chart(res=results, dwpi_code=dwpi_code, years=years, indicator=indicator,
            #                title=f'{indicator.title()} of {dwpi_code} over time', show=True)
            # else:
            #     line_chart(res=results, dwpi_code=dwpi_code, years=years, indicator=indicator,
            #                title=f'{indicator.title()} of {dwpi_code} over time')

    # densities=[]
    # for year in results.keys():
    #     densities.append((year, results[year]['density']))
    # x = list(map(lambda x: x[0], densities))
    # y = list(map(lambda x: x[1], densities))
    # x = np.array(x)
    # y = np.array(y)
    #
    # plt.plot(x, y, marker='o')
    # plt.title('DENSITY')
    # plt.show()

    print('Main done.')

# ----------------------------------------------------------------------------------------------------------------------