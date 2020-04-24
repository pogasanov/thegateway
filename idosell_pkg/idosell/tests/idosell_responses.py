SUCCESSFUL_AUTHORIZATION_RESPONSE = {
    "results": {"url": "http://testurl.com/export_successful"},
    "errors": {"faultCode": 0, "faultString": ""},
}
INVALID_AUTHORIZATION_RESPONSE = {"errors": {"faultCode": 1, "faultString": "Logowanie nie powiodło się"}}
FULL_URL = """<?xml version="1.0" encoding="UTF-8"?>
<provider_description file_format="IOF" version="3.0" generated_by="IdoSell Shop" generated="2020-04-14 13:54:00">
    <meta>
        <long_name><![CDATA[Strona demonstracyjna STANDARD Fashion]]></long_name>
        <short_name><![CDATA[demo46-pl-shop3]]></short_name>
        <showcase_image url="http://demo46-pl-shop3.yourtechnicaldomain.com/data/system/panel_logo.png"/>
        <email><![CDATA[no-reply@idosell.com]]></email>
        <tel><![CDATA[+48 91 443 66 00]]></tel>
        <fax><![CDATA[]]></fax>
        <www><![CDATA[demo46-pl-shop3.yourtechnicaldomain.com]]></www>
        <address>
            <street><![CDATA[Aleja Piastów 30]]></street>
            <zipcode><![CDATA[71-064]]></zipcode>
            <city><![CDATA[Szczecin]]></city>
            <country><![CDATA[Polska]]></country>
            <province><![CDATA[]]></province>
        </address>
        <time>
            <offer created="2020-04-14 13:54:00"/>
            <offer expires="2020-04-21 13:54:00"/>
        </time>
    </meta>
    <full url="http://testurl.com/export_successful_xml_full" changed="2020-04-11 20:01:14"></full>
    <light url="http://testurl.com/export_successful_xml_short"/>
</provider_description>
"""

PRODUCTS_XML = """<?xml version="1.0" encoding="utf-8"?>
<offer file_format="IOF" version="3.0" generated_by="IdoSell Shop" generated="2020-04-03 04:06:23" expires="2020-04-04 04:06:23" extensions="yes">
  <products xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml" language="pol" currency="PLN">
            <product type="regular" id="15" vat="23.0" site="3" currency="PLN">
            <producer id="1513170626" name="H&amp;M"/>
            <category id="0" name="*Kategoria tymczasowa"/>
            <unit id="0" name="szt."/>
            <card xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                  url="https://demo46-pl-shop3.yourtechnicaldomain.com/product-pol-15-Bluzka-damska-H-M.feed10005.html"/>
            <description>
                <name type="name" xml:lang="pol"><![CDATA[Bluzka damska H&M]]></name>
                <short_desc xml:lang="pol">
                    <![CDATA[Bluzka damska  H&M z długim rękawem, ciekawymi rozcięciami na ramionach]]></short_desc>
                <long_desc xml:lang="pol"></long_desc>
            </description>
            <iaiext:delivery_time xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml" unit="day"
                                  value="0">
                <iaiext:mode type="deliverer"/>
                <iaiext:time days="0"/>
            </iaiext:delivery_time>
            <iaiext:visibility xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:price_comparator visible="yes"/>
            </iaiext:visibility>
            <price gross="115" net="93.5"/>
            <srp gross="0" net="0"/>
            <iaiext:price_retail xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="115" net="93.5"/>
            </iaiext:price_retail>
            <iaiext:price_wholesale xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="115" net="93.5"/>
            </iaiext:price_wholesale>
            <iaiext:price_minimal xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="0" net="0"/>
            </iaiext:price_minimal>
            <sizes>
                <size available="unavailable" id="2" name="XS" panel_name="xs" code="15-2" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="in_stock" id="3" name="S" panel_name="s" code="15-3" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                    <stock id="0" quantity="-1" availability_id="1" available_stock_quantity="-1"/>
                    <stock id="1" quantity="-1" availability_id="1" available_stock_quantity="-1"/>
                </size>
                <size available="in_stock" id="4" name="M" panel_name="m" code="15-4" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                    <stock id="0" quantity="6" availability_id="1" available_stock_quantity="6"/>
                    <stock id="1" quantity="2" availability_id="2" available_stock_quantity="2"/>
                </size>
                <size available="in_stock" id="5" name="L" panel_name="l" code="15-5" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                    <stock id="0" quantity="-1" availability_id="1" available_stock_quantity="-1"/>
                    <stock id="1" quantity="-1" availability_id="1" available_stock_quantity="-1"/>
                </size>
                <size available="in_stock" id="6" name="XL" panel_name="xl" code="15-6" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                    <stock id="0" quantity="-1" availability_id="1" available_stock_quantity="-1"/>
                    <stock id="1" quantity="-1" availability_id="1" available_stock_quantity="-1"/>
                </size>
            </sizes>
            <images>
                <large>
                    <image url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/pictures/large/5/1/15_2.jpg"
                           changed="2019-03-28 13:27:35" hash="22e26b9aa278f065336b01c54d4d8a29" width="998"
                           height="1500"/>
                </large>
                <icons>
                    <icon url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/icons/large/5/1/15.jpg"
                          changed="2019-10-16 12:52:56" hash="8aba7b669087f5570a04f164aac0bd25" width="233"
                          height="350"/>
                    <group_icon url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/icons/versions/5/1/15.jpg"
                                changed="2019-10-16 12:52:56" hash="8aba7b669087f5570a04f164aac0bd25" width="133"
                                height="200"/>
                </icons>
            </images>
            <parameters>
                <parameter type="parameter" id="26" priority="0" distinction="n" group_distinction="y" hide="n"
                           auction_template_hide="n" xml:lang="pol" name="Kolor">
                    <value id="45" priority="0" xml:lang="pol" name="Szary"/>
                </parameter>
                <parameter type="parameter" id="16" priority="1" distinction="n" group_distinction="n" hide="n"
                           auction_template_hide="n" xml:lang="pol" name="Kruszec">
                    <value id="43" priority="0" xml:lang="pol" name="Kaszmir"/>
                    <value id="44" priority="1" xml:lang="pol" name="Bawełna"/>
                </parameter>
            </parameters>
            <group id="16" first_product_id="15">
                <group_by_parameter id="050ef565b4fad5b7faf128b67a873c71">
                    <name xml:lang="pol"><![CDATA[Kolor]]></name>
                    <product_value id="dbe83c17e44962cf54814fe61092f288">
                        <name xml:lang="pol"><![CDATA[Szary]]></name>
                    </product_value>
                </group_by_parameter>
            </group>
            <iaiext:sell_by xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:retail quantity="1"/>
                <iaiext:wholesale quantity="1"/>
            </iaiext:sell_by>
            <iaiext:inwrapper xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml" quantity="1"/>
        </product>
        <product type="regular" id="16" vat="23.0" site="3" currency="PLN">
            <producer id="1513170626" name="H&amp;M"/>
            <category id="0" name="*Kategoria tymczasowa"/>
            <unit id="0" name="szt."/>
            <card xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                  url="https://demo46-pl-shop3.yourtechnicaldomain.com/product-pol-16-Bluzka-damska-H-M.feed10005.html"/>
            <description>
                <name type="name" xml:lang="pol"><![CDATA[Bluzka damska H&M]]></name>
                <short_desc xml:lang="pol">
                    <![CDATA[Bluzka damska  H&M z długim rękawem, ciekawymi rozcięciami na ramionach]]></short_desc>
                <long_desc xml:lang="pol"></long_desc>
            </description>
            <iaiext:visibility xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:price_comparator visible="yes"/>
            </iaiext:visibility>
            <price gross="115" net="93.5"/>
            <srp gross="0" net="0"/>
            <iaiext:price_retail xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="115" net="93.5"/>
            </iaiext:price_retail>
            <iaiext:price_wholesale xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="115" net="93.5"/>
            </iaiext:price_wholesale>
            <iaiext:price_minimal xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="0" net="0"/>
            </iaiext:price_minimal>
            <sizes>
                <size available="unavailable" id="2" name="XS" panel_name="xs" code="16-2" weight="0">
                    <price gross="1518" net="1234">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="3" name="S" panel_name="s" code="16-3" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="4" name="M" panel_name="m" code="16-4" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="5" name="L" panel_name="l" code="16-5" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="6" name="XL" panel_name="xl" code="16-6" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
            </sizes>
            <images>
                <large>
                    <image url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/pictures/large/6/1/16_1.jpg"
                           changed="2019-03-28 13:27:32" hash="6e5b4cccd2d050d6821d640c46fbb35b" width="998"
                           height="1500"/>
                    <image url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/pictures/large/6/1/16_2.jpg"
                           changed="2019-03-28 13:27:33" hash="4363162c58e6ad4eb29e5f8981065661" width="998"
                           height="1500"/>
                </large>
                <icons>
                    <icon url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/icons/large/6/1/16.jpg"
                          changed="2019-10-16 12:52:56" hash="93a1c12b1f9508b9e5ba006ccac04b9e" width="233"
                          height="350"/>
                    <group_icon url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/icons/versions/6/1/16.jpg"
                                changed="2019-10-16 12:52:56" hash="93a1c12b1f9508b9e5ba006ccac04b9e" width="133"
                                height="200"/>
                </icons>
            </images>
            <parameters>
                <parameter type="parameter" id="26" priority="0" distinction="n" group_distinction="y" hide="n"
                           auction_template_hide="n" xml:lang="pol" name="Kolor">
                    <value id="42" priority="0" xml:lang="pol" name="Beżowy"/>
                </parameter>
                <parameter type="parameter" id="16" priority="1" distinction="n" group_distinction="n" hide="n"
                           auction_template_hide="n" xml:lang="pol" name="Kruszec">
                    <value id="44" priority="1" xml:lang="pol" name="Bawełna"/>
                </parameter>
            </parameters>
            <group id="16" first_product_id="15">
                <group_by_parameter id="050ef565b4fad5b7faf128b67a873c71">
                    <name xml:lang="pol"><![CDATA[Kolor]]></name>
                    <product_value id="39c5a679037633e9e9ad95702276b332">
                        <name xml:lang="pol"><![CDATA[Beżowy]]></name>
                    </product_value>
                </group_by_parameter>
            </group>
            <iaiext:sell_by xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:retail quantity="1"/>
                <iaiext:wholesale quantity="1"/>
            </iaiext:sell_by>
            <iaiext:inwrapper xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml" quantity="1"/>
        </product></products>
</offer>"""

PRODUCT_XML = """
        <product type="regular" id="16" vat="23.0" site="3" currency="PLN">
            <producer id="1513170626" name="H&amp;M"/>
            <category id="0" name="*Kategoria tymczasowa"/>
            <unit id="0" name="szt."/>
            <card xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                  url="https://demo46-pl-shop3.yourtechnicaldomain.com/product-pol-16-Bluzka-damska-H-M.feed10005.html"/>
            <description>
                <name type="name" xml:lang="pol"><![CDATA[Bluzka damska H&M]]></name>
                <short_desc xml:lang="pol">
                    <![CDATA[Bluzka damska  H&M z długim rękawem, ciekawymi rozcięciami na ramionach]]></short_desc>
                <long_desc xml:lang="pol"></long_desc>
            </description>
            <iaiext:visibility xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:price_comparator visible="yes"/>
            </iaiext:visibility>
            <price gross="115" net="93.5"/>
            <srp gross="0" net="0"/>
            <iaiext:price_retail xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="115" net="93.5"/>
            </iaiext:price_retail>
            <iaiext:price_wholesale xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="115" net="93.5"/>
            </iaiext:price_wholesale>
            <iaiext:price_minimal xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:site id="3" size_id="0" gross="0" net="0"/>
            </iaiext:price_minimal>
            <sizes>
                <size available="unavailable" id="2" name="XS" panel_name="xs" code="16-2" weight="0">
                    <price gross="1518" net="1234">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="3" name="S" panel_name="s" code="16-3" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="4" name="M" panel_name="m" code="16-4" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="5" name="L" panel_name="l" code="16-5" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
                <size available="unavailable" id="6" name="XL" panel_name="xl" code="16-6" weight="0">
                    <price gross="115" net="93.5">
                        <price_marketplace_site id="10005">
                            <delivery_cost carrierId="51">
                                <prepayment gross="15.56" net="12.65"/>
                                <cash_on_delivery gross="15.9" net="12.93"/>
                            </delivery_cost>
                        </price_marketplace_site>
                    </price>
                    <srp gross="0" net="0"/>
                </size>
            </sizes>
            <images>
                <large>
                    <image url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/pictures/large/6/1/16_1.jpg"
                           changed="2019-03-28 13:27:32" hash="6e5b4cccd2d050d6821d640c46fbb35b" width="998"
                           height="1500"/>
                    <image url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/pictures/large/6/1/16_2.jpg"
                           changed="2019-03-28 13:27:33" hash="4363162c58e6ad4eb29e5f8981065661" width="998"
                           height="1500"/>
                </large>
                <icons>
                    <icon url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/icons/large/6/1/16.jpg"
                          changed="2019-10-16 12:52:56" hash="93a1c12b1f9508b9e5ba006ccac04b9e" width="233"
                          height="350"/>
                    <group_icon url="https://demo46-pl-shop3.yourtechnicaldomain.com/data/gfx/icons/versions/6/1/16.jpg"
                                changed="2019-10-16 12:52:56" hash="93a1c12b1f9508b9e5ba006ccac04b9e" width="133"
                                height="200"/>
                </icons>
            </images>
            <parameters>
                <parameter type="parameter" id="26" priority="0" distinction="n" group_distinction="y" hide="n"
                           auction_template_hide="n" xml:lang="pol" name="Kolor">
                    <value id="42" priority="0" xml:lang="pol" name="Beżowy"/>
                </parameter>
                <parameter type="parameter" id="16" priority="1" distinction="n" group_distinction="n" hide="n"
                           auction_template_hide="n" xml:lang="pol" name="Kruszec">
                    <value id="44" priority="1" xml:lang="pol" name="Bawełna"/>
                </parameter>
            </parameters>
            <group id="16" first_product_id="15">
                <group_by_parameter id="050ef565b4fad5b7faf128b67a873c71">
                    <name xml:lang="pol"><![CDATA[Kolor]]></name>
                    <product_value id="39c5a679037633e9e9ad95702276b332">
                        <name xml:lang="pol"><![CDATA[Beżowy]]></name>
                    </product_value>
                </group_by_parameter>
            </group>
            <iaiext:sell_by xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml">
                <iaiext:retail quantity="1"/>
                <iaiext:wholesale quantity="1"/>
            </iaiext:sell_by>
            <iaiext:inwrapper xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml" quantity="1"/>
        </product>
"""

PRODUCT_XML_WITHOUT_DESCRIPTION = """<product xmlns:ns0="http://www.iai-shop.com/developers/iof/extensions.phtml" currency="PLN" id="16212" site="1" type="regular" vat="23.0">\n      <producer id="1320334713" name="Triaction" />\n      <category id="0" name="*Kategoria tymczasowa" />\n      <unit id="0" name="szt." />\n      <card url="https://www.telimena.pl/product-pol-16212-Triaction-Sportowe-Etui.feed10008.html" />\n      <description>\n        <name type="name" xml:lang="pol">Triaction Sportowe Etui</name>\n      </description>\n      <ns0:delivery_time unit="minute" value="1">\n        <ns0:mode type="deliverer" />\n        <ns0:time days="1" />\n      </ns0:delivery_time>\n      <ns0:visibility>\n        <ns0:price_comparator visible="yes" />\n      </ns0:visibility>\n      <price gross="78" net="63.41" />\n      <srp gross="0" net="0" />\n      <ns0:price_retail>\n        <ns0:site gross="78" id="1" net="63.41" size_id="0" />\n      </ns0:price_retail>\n      <ns0:price_wholesale>\n        <ns0:site gross="78" id="1" net="63.41" size_id="0" />\n      </ns0:price_wholesale>\n      <ns0:price_minimal>\n        <ns0:site gross="0" id="1" net="0" size_id="0" />\n      </ns0:price_minimal>\n      <sizes>\n        <size available="in_stock" code="16212-355" id="355" name="uniwersalny" panel_name="99" weight="0" ns0:code_external="76024722-1245">\n          <price gross="78" net="63.41">\n            <price_marketplace_site id="10008">\n              <delivery_cost carrierId="100160">\n                <prepayment gross="15.24" net="12.39" />\n                <cash_on_delivery gross="16.25" net="13.21" />\n              </delivery_cost>\n            </price_marketplace_site>\n          </price>\n          <srp gross="0" net="0" />\n          <stock availability_id="2" available_stock_quantity="4" id="1" quantity="4" />\n          <stock availability_id="1" available_stock_quantity="1" id="2" quantity="1" />\n          <stock availability_id="2" available_stock_quantity="5" id="5" quantity="5" />\n          <stock availability_id="2" available_stock_quantity="5" id="6" quantity="5" />\n        </size>\n      </sizes>\n      <images>\n        <large>\n          <image changed="2020-01-08 12:54:57" hash="d9df8cf98d119ee501c4e2519d745a52" height="918" url="https://www.telimena.pl/data/gfx/pictures/large/2/1/16212_1.jpg" width="800" />\n        </large>\n        <icons>\n          <icon changed="2020-01-08 12:54:57" hash="55cdea90e0e778ebda5e3baa1f7ba681" height="310" url="https://www.telimena.pl/data/gfx/icons/large/2/1/16212.jpg" width="270" />\n          <auction_icon changed="2020-01-08 12:54:56" hash="55cdea90e0e778ebda5e3baa1f7ba681" height="918" url="https://www.telimena.pl/data/gfx/icons/auctions/2/1/16212.jpg" width="800" />\n          <group_icon changed="2020-01-08 12:54:56" hash="55cdea90e0e778ebda5e3baa1f7ba681" height="70" url="https://www.telimena.pl/data/gfx/icons/versions/2/1/16212.jpg" width="61" />\n        </icons>\n      </images>\n      <ns0:navigation>\n        <ns0:site id="1">\n          <ns0:menu id="1">\n            <ns0:item id="445" menu_id="1" textid="Triaction sportowe etui za 1z&#322;" ns0:priority_menu="25" />\n          </ns0:menu>\n          <ns0:menu id="2" />\n          <ns0:menu id="3" />\n          <ns0:menu id="4" />\n          <ns0:menu id="5" />\n        </ns0:site>\n      </ns0:navigation>\n      <ns0:sell_by>\n        <ns0:retail quantity="1" />\n        <ns0:wholesale quantity="1" />\n      </ns0:sell_by>\n      <ns0:inwrapper quantity="1" />\n    </product>\n    """
