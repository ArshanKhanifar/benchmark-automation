exctags -R --fields=+l --languages=python --python-kinds=-iv -f ./tags $(pip show packet-python | grep Location | sed 's/^.*: //') 

