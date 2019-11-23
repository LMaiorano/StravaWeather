from pydap.client import open_url

dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc')
var = dataset['SST']
data = var[0,10:14,10:14]
print(data.data)