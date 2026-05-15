import functions_framework
from utils import load_daily

@functions_framework.http
def run(request):
    load_daily()
    return "OK", 200