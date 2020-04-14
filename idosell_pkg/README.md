# IdoSell integration

### API Credentials
In order to connect with IdoSell Marketplace API we need login and password of a Marketplace API account
and shop url.

#### How to create a Marketplace API account:
1. Log into your IdoSell account
2. Select option `MARKETING I INTEGRACJE` from the menu
3. Select `Marketplaces`
4. Choose a required shop (click `wybierz` in the column `Operacje` next to the appropriate shop url)
5. Click `+ Dodaj nowy serwis` button
6. Select `Polska` from a list (click `wybierz` in the second column
next to `Polska`)
7. Click `wybierz` in the second column next to `Pozostałe (wymagające konfiguracji)` 
8. In the field `nazwa` write a name for a service 

![haslo](/uploads/7de1cb315f0cc4aa91679c5d3fcf854a/haslo.jpg) 


9. Create a password. Next to `Zmień hasło` select option: 
   - `nie` - password for Marketplace account will be the same as for admin panel
   - `tak` - create a new password. Next to `Hasło` write a new password and confirm it
   in `Potwierdź hasło`
10. Click `Zapisz` button to save and generate your login 
11. Choose `wybierz` button in a row with an appropriate service, then select `ustawienia`

![ustawienia](/uploads/467945cab49a4671e5b799edcb6ebac4/ustawienia.jpg)

12. Find your `login` - next to `Login wykorzystywany do komunikacji serwisu ze sklepem`


#### File generation
`Notice:` Marketplace API generates an XML file with products data, which can be downloaded **only once**. File is generated priodically.
You can set start time and periodicity:
1. Log into your IdoSell account
2. Select option `MARKETING I INTEGRACJE` from the menu
3. Select `Marketplaces`
4. Choose a required shop (click `wybierz` in the column `Operacje` next to the appropriate shop url)
5. Choose `wybierz` button in a row with an appropriate service, then select `ustawienia`
6. Find `Ustawienia godzin eksportu (wspólne dla wszystkich porównywarek i marketplaces)`

![eksport](/uploads/f93e76ef75df7c9bc18b8fde8798c7b5/eksport.jpg)

7. In the field `Pierwszą operację wykonuj codziennie o godz` set start time
8. In the field `Kolejne operacje wykonuj, aż do końca dnia, co wskazaną ilość godzin` set periodicity in hours (for example every 4 hours)
9. Click `Zapisz` button to save changes

 


