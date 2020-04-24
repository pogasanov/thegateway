# SHOPER #

## Example shop ##

shoper.pl let's you use demo page for 14 days for free.

API Documentation:
https://developers.shoper.pl/developers/appstore/registration

### Create user with acccess to webapi ###

https://www.shoper.pl/help/artykul/jak-w-shoperze-utworzyc-dostep-po-api/

Translated: 

1. After logging in to admin panel of your shop go to **Konfiguracja -> Administracja, system -> Administratorzy** 
and click on **dodaj grupę administratorów**

2. Name your group, choose the access type of: **dostęp do panelu administracyjnego i webapi *(or just webapi perhaps)***
and then save with **Zapisz**

3. Continue editing your group by choosing access type in tab **Uprawnienia**, then save.
It's enought to set **Asortyment (Stock)** and **Konfiguracja (Configuration)** to **Odczyt (read access)**.

4. In the tab **Administratorzy** add an administrator who will have access over the API.


Then the shoper importer needs a login and a password of a created user.

Then set this environment variables 

SHOPER_BASE_URL=http://shop.url

SHOPER_USERNAME

SHOPER_PASSWORD


### Stock update errors ###

##### Object is locked #####

```json
{
    "error": "temporarily_unavailable", 
    "error_description": "Object is locked"
}
```

This error may appear when product editor window is open or was not saved properly.
In that case try saving the product or log out from an administrator account.