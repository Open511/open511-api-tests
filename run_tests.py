import sys

import nose

from open511_api_tests.base import set_options

def main():
    if len(sys.argv) < 3:
        return print_usage()
    api_url = sys.argv.pop(1)
    endpoint_url = sys.argv.pop(1)
    if not (api_url.startswith('http') and endpoint_url.startswith('http')):
        return print_usage()
    set_options(api_url, endpoint_url)

    nose.main()

def print_usage():
    sys.stderr.write("USAGE: python run_tests.py http://open511-discovery-url http://open511-test-endpoint-url\n")

if __name__ == '__main__':
    main()