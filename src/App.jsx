import { useState } from 'react';

function App() {
  const [phone, setPhone] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const validatePhone = async () => {
    if (!phone.trim()) {
      setError('Por favor ingresa un número telefónico');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch(`http://localhost:5000/api/phone-lookup?phone=${encodeURIComponent(phone)}`);
      if (!response.ok) {
        throw new Error('Error al validar el número');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <div className="container">
          <div className="logo">PhoneValidator</div>
          <ul className="nav-links">
            <li><a href="#home">Inicio</a></li>
            <li><a href="#pricing">Precios</a></li>
            <li><a href="#contact">Contacto</a></li>
          </ul>
        </div>
      </nav>

      {/* Hero */}
      <section id="home" className="hero">
        <div className="container">
          <h1>Valida números telefónicos a nivel mundial</h1>
          <p>Obtén país, operador y tipo de línea en segundos</p>
          <div className="input-group">
            <input
              type="text"
              placeholder="+18095551234"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <button onClick={validatePhone} disabled={loading}>
              {loading ? 'Validando...' : 'Validar número'}
            </button>
          </div>
        </div>
      </section>

      {/* Results */}
      <section className="results">
        <div className="container">
          {loading && <div className="loading">Validando número...</div>}
          {error && <div className="error">{error}</div>}
          {result && (
            <div className="card">
              <h3>Resultado de Validación</h3>
              <div className="field">
                <strong>¿Es válido?</strong> {result.valid ? 'Sí' : 'No'}
              </div>
              <div className="field">
                <strong>País:</strong> {result.country || 'N/A'}
              </div>
              <div className="field">
                <strong>Operador:</strong> {result.carrier || 'N/A'}
              </div>
              <div className="field">
                <strong>Tipo de línea:</strong> {result.lineType || 'N/A'}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Benefits */}
      <section className="benefits">
        <div className="container">
          <h2>Beneficios</h2>
          <div className="grid">
            <div className="benefit">
              <h3>Validación en tiempo real</h3>
              <p>Obtén resultados instantáneos con nuestra API rápida y confiable.</p>
            </div>
            <div className="benefit">
              <h3>Cobertura internacional</h3>
              <p>Soporte para números telefónicos de más de 200 países.</p>
            </div>
            <div className="benefit">
              <h3>Ideal para empresas</h3>
              <p>Perfecto para desarrolladores y empresas que necesitan validar números a gran escala.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="pricing">
        <div className="container">
          <h2>Precios</h2>
          <div className="grid">
            <div className="plan">
              <h3>Free</h3>
              <div className="price">$0/mes</div>
              <ul>
                <li>100 validaciones/mes</li>
                <li>Soporte básico</li>
                <li>API REST</li>
              </ul>
              <button>Comenzar</button>
            </div>
            <div className="plan">
              <h3>Pro</h3>
              <div className="price">$29/mes</div>
              <ul>
                <li>10,000 validaciones/mes</li>
                <li>Soporte prioritario</li>
                <li>Enriquecimiento de datos</li>
              </ul>
              <button>Comenzar</button>
            </div>
            <div className="plan">
              <h3>Empresa</h3>
              <div className="price">Personalizado</div>
              <ul>
                <li>Validaciones ilimitadas</li>
                <li>Soporte dedicado</li>
                <li>Integración personalizada</li>
              </ul>
              <button>Contactar</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 PhoneValidator. Todos los derechos reservados.</p>
          <p>Política de privacidad | Términos de servicio</p>
        </div>
      </footer>
    </div>
  );
}

export default App;