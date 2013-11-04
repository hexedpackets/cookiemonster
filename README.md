cookiemonster
=============

A covert channel over HTTP using Google Analytic cookies as the medium.  This provides a bidirectional channel of 33 characters/ssecond in each direction.

## Notes on specific cookies and examples
### __utmb
* 10^22 - really 10^14
* expires after 30 minutes
* timestamp of when user enters site
* 87498951.2.10.1301411309
* .2. increases by 2 every reload
* expiration also updates

### __utmc
* 10^8
* session cookie
* timestamp of when user leaves site
* matches first 8 of all other cookies
* 87498951

### __utma
* persistant
* number of times user has visited site, first visit, and last visit
* 87498951.916881531.1301411309.1301411309.1301411309.1
* 8.9.10.10.10.1
* 10^49

### __utmz
* 6 month expiration
* allows customized length
* where user came from, browser, link clicked, etc.
* 87498951.1301411309.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)
* 10^14

### __utmv
* persistant
* custom segmentation for website
