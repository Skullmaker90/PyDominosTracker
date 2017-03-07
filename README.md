# PyDominosTracker
A python script build to check and track Dominos orders via phone number.

This script is designed to periodically query the dominos public order tracking api for
orders stored under specific phone numbers, then post to prowl with the results of said
order or a return statement with no orders found and a list of numbers that failed the 
check. Requirements are:

`Beautiful Soup via bs4`
`Requests`
`Prowl`

The script should can be ran by cron by adding `0,30 * * * * python /path/to/dominos.py`

Future updates to script could be to store order history in a database and create a web
frontend as a service.
