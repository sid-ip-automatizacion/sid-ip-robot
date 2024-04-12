import requests

class AccessPoint():
    def __init__(self, vendor):
        self.vendor = vendor
        self.model = ''
        self.name = ''
        self.description = ''
        self.mac = ''
        self.serial = ''
        self.ip = ''
        self.controller_ip = ''
        self.site = ''
        self.status = ''
        self.clients = 0

    def config_infoap_meraki(self, api_key):
        """
        Configura el nombre del AP en el portal de Meraki
        """
        myheaders = {
            'x-cisco-meraki-api-key': api_key
        }
        mybody = {"name": self.name, "notes": self.description, "address": self.site, "moveMapMarker": True}
        print("configurar nombre {}, descripcion {}, y ubicacion {} en portal meraki para ap serial {}".
              format(self.name, self.description, self.site, self.mac))
        response = requests.request('PUT', 'https://api.meraki.com/api/v1/devices/{}'.format(self.serial),
                                    headers=myheaders, data=mybody)
        print(response)

    def config_infoap_ruckus_sz(self, serviceTicket, apiversion):
        """
        Configura el nombre, descripcion, y location del AP en la Ruckus virtualSmartZone
        """
        param_st = {'serviceTicket': serviceTicket}
        print("configurar nombre {}, descripcion {} y ubicacion {} en la smartzone para ap mac {}".
              format(self.name, self.description, self.site, self.mac))
        requests.patch(
            'https://{SZip}/wsg/api/public/{apiver}/aps/{mac}'.format(SZip=self.controller_ip, apiver=apiversion,
                                                                      mac=self.mac), params=param_st,
            json={'name': self.name, 'description': self.description, 'location': self.site}, verify=False, timeout=10)

    def config_infoap_fortinet(self, api_key, fgtIP):
        """
        Configura el nombre del AP en el fotigate
        """
        body = {'name': self.name, 'location': self.description}
        session = requests.Session()
        my_message = session.put("https://{fIP}/api/v2/cmdb/wireless-controller/wtp/{serial}?vdom=*&access_token="
                                 "{key}".format(fIP=fgtIP, serial=self.serial, key=api_key), json=body, verify=False)
        print(my_message.status_code)
        print(my_message.json())

    def config_ap(self, SZserviceTicket='not_set', SZapiversion='note_set', meraki_api_key='not_set', forti_api_key='not_set', forti_IP='not_set'):
        """
        Especifica el nombre y descripción del AP en la controladora
        """
        if self.vendor == 'meraki':
            self.config_infoap_meraki(meraki_api_key)
        elif self.vendor == 'ruckus_vsz' or self.vendor == 'ruckus_sz_onsite':
            self.config_infoap_ruckus_sz(SZserviceTicket, SZapiversion)
        elif self.vendor == 'fortinet':
            self.config_infoap_fortinet(forti_api_key, forti_IP)
        else:
            print("error: vendor desconocido")


if __name__ == '__main__':
    ap = AccessPoint('Ruckus_vsz')
    ap.model = ''
    ap.name = 'NombrePython'
    ap.description = 'Descripcion desde Python'
    ap.mac = 'EC:58:EA:0A:46:60'
    ap.serial = '201809000219'
    ap.ip = ''
    ap.config_name_ruckus_sz()