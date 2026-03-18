import robot from '../assets/robot.png'
import {
  homeSectionStyle,
  homeLeftStyle,
  homeTitleStyle,
  homeDescriptionStyle,
  homeButtonStyle,
  homeRightStyle,
  homeRobotStyle
} from '../helpers/styles'
import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate()

  return (
    <section style={homeSectionStyle}>
      <div style={homeLeftStyle}>
        <h1 style={homeTitleStyle}>
          Trace the
          Transformation of 
          AI-Generated Text
        </h1>

        <p style={homeDescriptionStyle}>
          HumanizeTrace lets you generate AI text, apply different humanization tools,
          and analyze how the meaning, tone, and structure evolve through the transformation pipeline.
        </p>

        <button style={homeButtonStyle} onClick={() => navigate('/input')}>
          Starts Now
        </button>
      </div>

      <div style={homeRightStyle}>
        <img src={robot} alt="Robot" style={homeRobotStyle} />
      </div>
    </section>
  )
}

export default Home