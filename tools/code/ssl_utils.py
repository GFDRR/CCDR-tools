import ssl
import requests
import urllib3
import warnings

def disable_ssl_verification():
    """
    Comprehensively disable SSL verification for all HTTP libraries used in the application.
    This should be used only in environments where proper SSL verification isn't possible.
    """
    # Disable warnings about insecure requests
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Patch the SSL context creation
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Set the default for all requests
    context = ssl.create_default_context()
    context.set_ciphers('HIGH:!DH:!aNULL')
    
    # Monkey patch the requests package
    old_merge_environment_settings = requests.Session.merge_environment_settings
    
    def new_merge_environment_settings(self, url, proxies, stream, verify, cert):
        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False
        return settings
    
    requests.Session.merge_environment_settings = new_merge_environment_settings
    
    print("SSL verification has been disabled for this session.")
