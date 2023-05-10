import bcrypt
import json




x = input('ingrese password...  ')
print(x)
'''
if bcrypt.checkpw(x.encode('utf-8'),hashed):
    print('acceso ok')
else:
    print('falla autenticacion')
'''
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(x.encode('utf-8'),salt)


dict={
    'username':'amolano',
    'password':hashed.decode()
}


json_file = json.dumps(dict, indent=4)
 
# Writing to sample.json
with open("credentials.json", "w") as outfile:
    outfile.write(json_file)

p = list(dict.values())[1].encode('utf-8')
print(p)
print(bcrypt.checkpw(p,hashed))
print(list(dict.values())[1].encode('utf-8'))


if bcrypt.checkpw(p,hashed):
    print('acceso ok')
else:
    print('falla autenticacion')