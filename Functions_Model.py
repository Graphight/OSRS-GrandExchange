import itertools
import statsmodels.api as sm


def determine_best_p_d_q_variables(sample_data):
    p = d = q = range(0, 2)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
    options = dict()
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                model = sm.tsa.statespace.SARIMAX(sample_data,
                                                  order=param,
                                                  seasonal_order=param_seasonal,
                                                  enforce_stationarity=False,
                                                  enforce_invertibility=False)
                results = model.fit(disp=False)
                options[results.aic] = [param, param_seasonal]
                # print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
            except Exception as e:
                print(e)
    # Determine the best formation to use
    best = min(options.keys())
    print("\nThe lowest scoring item returned < {} > which had the params < {} >\n".format(best, options[best]))
    # Use this configuration
    order = options[best][0]
    seasonal_order = options[best][1]
    model = sm.tsa.statespace.SARIMAX(sample_data,
                                      order=order,
                                      seasonal_order=seasonal_order,
                                      enforce_stationarity=False,
                                      enforce_invertibility=False)
    return model