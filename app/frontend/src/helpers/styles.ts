
import { WHITE, GREY, BLACK, PRIMARY } from './colors'

export const FONTS = [
    'Open Sans',
    'Poppins',
    'Roboto', 
    'sans-serif',
]

// Header styles

export const headerStyle = {
  position: 'fixed' as const,
  top: 0,
  left: 0,
  right: 0,
  display: 'flex' as const,
  justifyContent: 'space-between' as const,
  alignItems: 'center' as const,
  padding: '1rem 2rem',
  backgroundColor: WHITE,
  borderBottom: '1px solid' + GREY,
  zIndex: 1000
}

export const headerLeftStyle = {
  display: 'flex' as const,
  alignItems: 'center' as const
}

export const logoStyle = {
  width: '200px',
  height: 'auto'
}

export const navStyle = {
  display: 'flex' as const,
  gap: '2rem'
}

export const navLinkStyle = {
  textDecoration: 'none' as const,
  color: BLACK,
  fontSize: '1rem'
}

// Home styles

export const homeSectionStyle = {
  minHeight: 'calc(100vh - 84px)',
  backgroundColor: GREY,
  width: '100%',
  display: 'flex' as const,
  justifyContent: 'space-between' as const,
  alignItems: 'center' as const,
  padding: '3rem 5rem',
  marginLeft: 0,
}

export const homeLeftStyle = {
  maxWidth: '620px',
  display: 'flex' as const,
  flexDirection: 'column' as const,
  alignItems: 'flex-start' as const,
  textAlign: 'left' as const
}

export const homeTitleStyle = {
  fontSize: '60px',
  color: BLACK,
  margin: 0,
  textAlign: 'left' as const
}

export const homeDescriptionStyle = {
  marginTop: '2rem',
  fontSize: '20px',
  lineHeight: 1.35,
  color: PRIMARY,
  textAlign: 'left' as const
}

export const homeButtonStyle = {
  marginTop: '2.5rem',
  backgroundColor: BLACK,
  color: WHITE,
  border: 'none',
  borderRadius: '10px',
  padding: '14px 36px',
  minWidth: '200px',
  fontSize: '15px',
  fontFamily: "'Open Sans', sans-serif",
  cursor: 'pointer'
}

export const homeRightStyle = {
  display: 'flex' as const,
  justifyContent: 'center' as const,
  alignItems: 'center' as const,
  flex: 1
}

export const homeRobotStyle = {
  width: '560px',
  maxWidth: '100%',
  height: 'auto'
}

// Essay Input styles
export const essayInputSectionStyle = {
  width: '100%',
  minHeight: 'calc(100vh - 84px)', 
  backgroundColor: GREY,
  padding: '3rem 2rem',
  display: 'flex' as const,
  justifyContent: 'center' as const,
  alignItems: 'flex-start' as const,
  marginTop: '84px' // Header height
}

export const essayInputCardStyle = {
  width: '100%',
  maxWidth: '1200px',
  backgroundColor: WHITE,
  borderRadius: '16px',
  padding: '2rem 2.5rem',
  boxShadow: '0 8px 30px rgba(0, 0, 0, 0.05)'
}

export const essayInputTitleStyle = {
  margin: '0 0 2rem 0',
  color: BLACK,
  fontSize: '24px',
  fontWeight: 600,
  textAlign: 'center' as const
}

export const essayInputRowStyle = {
  display: 'flex' as const,
  gap: '2rem'
}

export const essayColumnStyle = {
  flex: 1,
  display: 'flex' as const,
  flexDirection: 'column' as const
}

export const essayLabelStyle = {
  display: 'flex' as const,
  justifyContent: 'space-between' as const,
  alignItems: 'center' as const,
  marginBottom: '0.75rem',
  color: BLACK,
  fontWeight: 500,
  fontSize: '16px'
}

export const essayPasteButtonStyle = {
  backgroundColor: 'transparent',
  color: PRIMARY,
  border: 'none',
  borderRadius: '6px',
  padding: '4px 8px',
  cursor: 'pointer',
  fontWeight: 600,
  fontSize: '14px'
}

export const essayTextareaStyle = {
  flex: 1,
  minHeight: '400px',
  border: `1px solid #E0E0E0`,
  backgroundColor: '#FCFCFC',
  borderRadius: '8px',
  padding: '1rem',
  fontSize: '16px',
  fontFamily: "'Open Sans', sans-serif",
  resize: 'vertical' as const,
  outlineColor: PRIMARY
}

export const essayInputFooterStyle = {
  display: 'flex' as const,
  justifyContent: 'flex-end' as const,
  marginTop: '2rem',
  paddingTop: '1.5rem',
  borderTop: `1px solid ${GREY}`
}

export const essayAnalyzeButtonStyle = {
  backgroundColor: PRIMARY,
  color: WHITE,
  border: 'none',
  borderRadius: '8px',
  padding: '14px 32px',
  fontSize: '16px',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'opacity 0.2s'
}