
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
  cursor: 'pointer',
  transition: 'transform 0.2s ease-in-out, background-color 0.2s ease'
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

// TODO: Make these styles more modular and reusable across the app, overview Card Styles overall

// Essay Input styles
export const essayInputSectionStyle = {
  width: '100%',
  minHeight: 'calc(100vh - 84px)', 
  backgroundColor: GREY,
  display: 'flex' as const,
  justifyContent: 'center' as const,
  alignItems: 'center' as const,
  marginTop: '80px' 
}

export const essayInputCardStyle = {
  width: '100%',
  margin: '50px',
  backgroundColor: WHITE,
  borderRadius: '16px',
  padding: '2rem 2.5rem',
  boxShadow: '0 8px 30px rgba(0, 0, 0, 0.05)'
}

export const essayInputTitleStyle = {
  margin: '0 0 3rem 0',
  color: BLACK,
  fontSize: '30px',
  marginBottom: '2.5rem',
  fontWeight: 700,
  textAlign: 'left' as const,
  paddingBottom: '0.5rem',
  borderBottom: `2px solid ${GREY}`,
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
  color: PRIMARY,
  border: `1px solid ${GREY}`,
  backgroundColor: 'transparent',
  borderRadius: '10px',
  padding: '4px 8px',
  cursor: 'pointer',
  fontWeight: 600,
  fontSize: '14px'
}

export const essayTextareaStyle = {
  flex: 1,
  minHeight: '300px',
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
  transition: 'opacity 0.2s',
  fontFamily: "'Open Sans', sans-serif",
}

// Result styles
export const pageStyle = {
  padding: '2rem',
  marginTop: '80px', 
  backgroundColor: GREY,
  minHeight: 'calc(100vh - 84px)',
}


export const cardStyle = {
  backgroundColor: WHITE,
  padding: '1.5rem 2rem',
  borderRadius: '16px',
  boxShadow: `0 4px 20px ${GREY}`,
  border: `1px solid ${GREY}`,
}

export const errorStyle = {
  textAlign: 'center',
  color: BLACK
}

export const titleStyle = {
  color: BLACK,
  borderBottom: `1px solid ${GREY}`,
  paddingBottom: '1rem',
  marginBottom: '1.5rem',
  fontSize: '1.5rem'
}

// Result Card Styles

export const resultHeaderStyle = {
  marginBottom: '1.25rem',
}

export const resultSubtitleStyle = {
  margin: '0.5rem 0 0 0',
  color: BLACK,
  opacity: 0.7,
  fontSize: '0.95rem',
  lineHeight: 1.5,
}

export const resultOverviewGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
  gap: '1rem',
  marginBottom: '1.5rem',
}

export const resultStatCardStyle = {
  backgroundColor: WHITE,
  border: `1px solid ${GREY}`,
  borderRadius: '14px',
  padding: '1rem',
  minHeight: '145px',
}

export const resultStatTopRowStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '0.75rem',
  gap: '0.5rem',
}

export const resultStatTitleStyle = {
  fontSize: '1rem',
  fontWeight: 700,
  color: BLACK,
  margin: 0,
}

export const resultChipStyle = {
  fontSize: '0.72rem',
  fontWeight: 600,
  padding: '0.3rem 0.65rem',
  borderRadius: '999px',
  backgroundColor: GREY,
  color: BLACK,
  whiteSpace: 'nowrap',
}

export const resultStatValueStyle = {
  fontSize: '1.9rem',
  fontWeight: 800,
  color: BLACK,
  marginBottom: '0.65rem',
  lineHeight: 1,
}

export const resultStatDescriptionStyle = {
  fontSize: '0.88rem',
  color: BLACK,
  opacity: 0.72,
  lineHeight: 1.45,
  marginTop: '0.65rem',
}

export const progressTrackStyle = {
  width: '100%',
  height: '10px',
  backgroundColor: '#E5E7EB',
  borderRadius: '999px',
  overflow: 'hidden',
}

export const tabRowStyle = {
  display: 'flex',
  gap: '0.75rem',
  flexWrap: 'wrap',
  marginBottom: '1.5rem',
}

export const tabButtonBaseStyle = {
  borderRadius: '10px',
  padding: '0.7rem 1rem',
  fontSize: '0.95rem',
  fontWeight: 700,
  cursor: 'pointer',
  fontFamily: "'Open Sans', sans-serif",
}

export const resultContentGridStyle = {
  display: 'grid',
  gridTemplateColumns: '1.45fr 1fr',
  gap: '1rem',
}

export const resultSectionCardStyle = {
  backgroundColor: WHITE,
  border: `1px solid ${GREY}`,
  borderRadius: '16px',
  overflow: 'hidden',
}

export const resultSectionHeaderStyle = {
  padding: '1.15rem 1.25rem',
  borderBottom: `1px solid ${GREY}`,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  gap: '1rem',
}

export const resultSectionTitleStyle = {
  margin: 0,
  fontSize: '1.15rem',
  fontWeight: 700,
  color: BLACK,
}

export const resultSectionDescriptionStyle = {
  margin: '0.35rem 0 0 0',
  fontSize: '0.92rem',
  color: BLACK,
  opacity: 0.72,
  lineHeight: 1.5,
}

export const resultSectionBodyStyle = {
  padding: '1.15rem 1.25rem',
}

export const metricRowStyle = {
  border: `1px solid ${GREY}`,
  borderRadius: '12px',
  padding: '0.95rem',
  marginBottom: '0.85rem',
}

export const metricRowTopStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: '0.75rem',
  marginBottom: '0.5rem',
}

export const metricLabelWrapStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.5rem',
  flexWrap: 'wrap',
}

export const metricLabelStyle = {
  fontSize: '1rem',
  fontWeight: 700,
  color: BLACK,
}

export const metricValueStyle = {
  fontSize: '1.05rem',
  fontWeight: 800,
  color: BLACK,
}

export const metricDescriptionStyle = {
  margin: '0.55rem 0 0 0',
  fontSize: '0.88rem',
  color: BLACK,
  opacity: 0.72,
  lineHeight: 1.45,
}

export const infoBoxStyle = {
  border: `1px solid ${GREY}`,
  borderRadius: '14px',
  padding: '1rem',
  backgroundColor: WHITE,
}

export const infoBoxTitleStyle = {
  margin: '0 0 0.75rem 0',
  fontSize: '1rem',
  fontWeight: 700,
  color: BLACK,
}

export const infoBoxTextStyle = {
  fontSize: '0.9rem',
  color: BLACK,
  opacity: 0.78,
  lineHeight: 1.55,
}

export const infoBoxStackStyle = {
  display: 'grid',
  gap: '1rem',
}

export const emotionRowStyle = {
  marginBottom: '0.85rem',
}

export const emotionRowTopStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '0.35rem',
  gap: '0.75rem',
}

export const emotionLabelStyle = {
  fontSize: '0.92rem',
  color: BLACK,
  textTransform: 'capitalize' as const,
}

export const emotionValueStyle = {
  fontSize: '0.9rem',
  fontWeight: 700,
  color: BLACK,
}