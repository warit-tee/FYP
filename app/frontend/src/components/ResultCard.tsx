import { useLocation, Link } from 'react-router-dom'
import { pageStyle, cardStyle, errorStyle, titleStyle } from '../helpers/styles'
import { PRIMARY } from '../helpers/colors'

function ResultCard() {
  const location = useLocation()
  const results = location.state?.results

  // Handle the case where a user navigates directly to this page without data
  if (!results) {
    return (
      <div style={pageStyle}>
        <div style={{ ...cardStyle, maxWidth: '800px', margin: '0 auto' }}>
          <div style={errorStyle}>
            <h2>No Analysis Data Found</h2>
            <p>Please go back and analyze two texts to see the results.</p>
            <Link to="/input" style={{ color: PRIMARY, textDecoration: 'none', fontWeight: 600 }}>
              Go to Input Page
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // If data exists, display it in a formatted way
  return (
    <div style={pageStyle}>
      <div style={{ ...cardStyle, maxWidth: '1000px', margin: '0 auto' }}>
        <h2 style={titleStyle}>Analysis Report</h2>
        <pre style={preStyle}>
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>
    </div>
  )
}

export default ResultCard