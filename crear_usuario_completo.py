"""
Script para crear un usuario completo en Supabase (Auth + Tabla)
"""
from dotenv import load_dotenv
import os
from supabase import create_client
import uuid

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print("=" * 80)
print("CREAR USUARIO COMPLETO EN SUPABASE")
print("=" * 80)

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Datos del usuario
email = "admin@sst.com"
password = "Admin123456"
nombre = "Administrador Sistema"
cargo = "Administrador"
area = "Seguridad y Salud"

print(f"\n📝 Creando usuario:")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Nombre: {nombre}")

try:
    # 1. Crear en Supabase Auth
    print("\n🔐 Paso 1: Creando en Supabase Auth...")
    
    auth_response = client.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True
    })
    
    if auth_response.user:
        auth_user_id = auth_response.user.id
        print(f"✅ Usuario Auth creado con ID: {auth_user_id}")
        
        # 2. Crear en tabla usuarios
        print("\n📊 Paso 2: Creando registro en tabla usuarios...")
        
        usuario_data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "nombre_completo": nombre,
            "cargo": cargo,
            "area": area,
            "telefono": "",
            "rol": "admin",
            "activo": True,
            "auth_user_id": auth_user_id
        }
        
        db_response = client.table("usuarios").insert(usuario_data).execute()
        
        if db_response.data:
            print(f"✅ Usuario registrado en BD con ID: {usuario_data['id']}")
            
            print("\n" + "=" * 80)
            print("✅ ¡USUARIO CREADO EXITOSAMENTE!")
            print("=" * 80)
            print(f"\n🔑 CREDENCIALES:")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"\n🌐 Ahora puedes hacer LOGIN en la app:")
            print(f"   1. Ejecuta: .\\reiniciar_completo.bat")
            print(f"   2. Abre: http://localhost:8501")
            print(f"   3. Inicia sesión con las credenciales de arriba")
            print("\n" + "=" * 80)
        else:
            print("❌ Error al crear registro en tabla usuarios")
    else:
        print("❌ Error al crear usuario en Auth")
        
except Exception as e:
    error_msg = str(e)
    
    if "User already registered" in error_msg or "already exists" in error_msg:
        print("\n⚠️  El usuario ya existe!")
        print(f"\n🔑 Puedes intentar iniciar sesión con:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n💡 O prueba con otro email modificando este script")
    else:
        print(f"❌ Error: {error_msg}")

print("\n" + "=" * 80)
