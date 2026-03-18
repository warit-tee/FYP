import logo from '../assets/logo.png'
import { headerStyle, headerLeftStyle, logoStyle, navStyle, navLinkStyle } from '../helpers/styles'

function Header() {
  return (
    <header style={headerStyle}>
      <div style={headerLeftStyle}>
        <img src={logo} alt="Logo" style={logoStyle} />
      </div>
      <nav style={navStyle}>
        <a href="/" style={navLinkStyle}>Home</a>
        <a href="/about" style={navLinkStyle}>About Us</a>
        <a href="/metrics" style={navLinkStyle}>Metrics</a>
        <a href="/contact" style={navLinkStyle}>Contact Us</a>
      </nav>
    </header>
  )
}

export default Header