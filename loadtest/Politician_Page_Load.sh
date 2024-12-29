DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
locust -f $DIR/PoliticianPageLoad.py --host=https://api.wevoteusa.org --users 100 --spawn-rate 100 --run-time 10m