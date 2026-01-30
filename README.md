# 📱 Phone Validation SaaS

Una plataforma SaaS completa para validación de números telefónicos con sistema de facturación integrado usando Stripe.

## ✨ Características

- 🔍 **Validación de Teléfonos**: Integración con NumLookup API
- 💳 **Sistema de Pagos**: Stripe para suscripciones y facturación automática
- 🔐 **Autenticación JWT**: Sistema seguro de login/registro
- 📊 **Dashboard**: Panel de control con métricas de uso
- 🏷️ **Planes de Suscripción**: Free, Pro, Enterprise con límites personalizados
- 🔄 **Rate Limiting**: Control de uso por usuario y plan
- 📧 **Webhooks**: Procesamiento automático de eventos de pago
- 🧾 **Facturación**: Invoices, refunds, y gestión de impuestos
- 📈 **Analytics**: Seguimiento de uso y métricas

## 🚀 Inicio Rápido

### 1. Clonar y Configurar

```bash
git clone <tu-repo>
cd phone-validation-saas
python setup.py
```

### 2. Configurar APIs

Edita el archivo `.env` con tus API keys:

```bash
# NumLookup API (https://numlookupapi.com)
NUMLOOKUP_API_KEY=tu_api_key_aqui

# Stripe (https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_tu_key
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret
```

### 3. Probar APIs

```bash
python test_apis.py
```

### 4. Iniciar Servidor

```bash
# Windows
start_server.bat

# Linux/Mac
./start_server.sh
```

Ve a http://localhost:8000/docs para la documentación interactiva.

## 📋 Requisitos

- Python 3.8+
- Redis (para rate limiting)
- SQLite/PostgreSQL

## 🏗️ Arquitectura

```
fastapi_backend/
├── app/
│   ├── main.py              # Punto de entrada
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión DB
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Lógica de negocio
│   ├── routes/              # Endpoints API
│   └── middleware/          # Middlewares
├── scripts/
│   └── init_db.py           # Inicialización DB
└── requirements.txt         # Dependencias
```

## 🔧 APIs Integradas

### NumLookup API
- Validación de números telefónicos
- Información de carrier y ubicación
- Detección de números válidos/inválidos

### Stripe
- Procesamiento de pagos
- Gestión de suscripciones
- Webhooks para eventos de facturación
- Refunds y gestión de invoices

## 📊 Endpoints Principales

### Autenticación
```
POST /auth/register     # Registro de usuario
POST /auth/login        # Login
GET  /auth/me          # Perfil de usuario
```

### Validación de Teléfonos
```
GET  /phone/lookup?phone=+1234567890    # Validación individual
POST /phone/lookup-batch                # Validación por lotes
```

### API Keys
```
POST /api-keys/create   # Crear API key
GET  /api-keys/list     # Listar keys
DELETE /api-keys/{id}   # Eliminar key
```

### Facturación
```
GET  /billing/invoices          # Listar invoices
GET  /billing/invoices/{id}     # Detalle invoice
POST /billing/refund            # Crear refund
PUT  /billing/tax-info          # Actualizar info fiscal
```

### Dashboard
```
GET /dashboard/stats    # Estadísticas de uso
GET /dashboard/usage    # Historial de uso
```

## 💰 Planes de Suscripción

| Plan | Precio | Validaciones/Mes | Rate Limit |
|------|--------|------------------|------------|
| Free | $0 | 100 | 10/min |
| Pro | $9.99 | 10,000 | 100/min |
| Enterprise | $49.99 | 100,000 | 500/min |

## 🔒 Seguridad

- Autenticación JWT con expiración
- Rate limiting por usuario y endpoint
- Validación de entrada con Pydantic
- Hashing de contraseñas con bcrypt
- Verificación de firmas en webhooks
- CORS configurado

## 🧪 Testing

```bash
# Ejecutar pruebas de APIs
python test_apis.py

# Ejecutar tests unitarios (cuando estén disponibles)
pytest
```

## 📚 Documentación

- [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Guía completa de configuración
- [http://localhost:8000/docs](http://localhost:8000/docs) - Documentación interactiva (FastAPI)
- [http://localhost:8000/redoc](http://localhost:8000/redoc) - Documentación alternativa

## 🚀 Despliegue

### Desarrollo
```bash
uvicorn app.main:app --reload
```

### Producción
```bash
# Usando Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Próximamente)
```bash
docker build -t phone-validation-saas .
docker run -p 8000:8000 phone-validation-saas
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

- 📧 Email: support@phonevalidation.com
- 💬 Discord: [Únete a nuestro servidor](https://discord.gg/phonevalidation)
- 🐛 Issues: [GitHub Issues](https://github.com/tu-repo/issues)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Stripe](https://stripe.com/) - Plataforma de pagos
- [NumLookup](https://numlookupapi.com/) - API de validación telefónica
- [SQLAlchemy](https://sqlalchemy.org/) - ORM de Python

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!