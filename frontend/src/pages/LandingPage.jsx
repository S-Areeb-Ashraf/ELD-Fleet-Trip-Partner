// import React from 'react';
// import { useNavigate } from 'react-router-dom';
// import { Truck, ArrowRight } from 'lucide-react';

// export default function LandingPage() {
//   const navigate = useNavigate();

//   return (
//     <main className="landing-page">
//       <div className="landing-backdrop" aria-hidden="true">
//         <div className="landing-backdrop-glow" />
//         <div className="landing-backdrop-road" />
//         <div className="landing-backdrop-truck">
//           <Truck size={160} strokeWidth={1.2} />
//         </div>
//       </div>

//       <section className="landing-content" aria-label="Welcome screen">
//         <div className="landing-badge">Spotter ELD Fleet Trip Planner</div>
//         <h1 className="landing-title">Welcome</h1>
//         <p className="landing-copy">
//           Hi, Plan your Trip with Us.
//           {/* Plan FMCSA-compliant routes, generate turn-by-turn navigation, and create daily log sheets in one flow. */}
//         </p>
//         <button type="button" className="landing-cta btn btn-primary" onClick={() => navigate('/plan')}>
//           Create trip with us
//           <ArrowRight size={18} />
//         </button>
//       </section>
//     </main>
//   );
// }

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <main className="landing-page">
      {/* Background Image Container */}
      <div className="landing-backdrop" aria-hidden="true">
        <img
          src="https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=1920&q=80" // Place your image URL or path here
          alt="Truck on highway"
          className="landing-bg-image"
        />
        {/* Dark overlay to keep text legible */}
        <div className="landing-backdrop-overlay" />
      </div>

      {/* Main Card Content */}
      <section className="landing-content" aria-label="Welcome screen">
        <div className="landing-badge"> ELD Fleet Trip Planner</div>
        {/* <div className="landing-badge">Welcome</div> */}
        <h1 className="landing-title">Welcome</h1>
        {/* <p className="landing-copy">
          Hi, Plan your Trip with Us.
        </p> */}
        <button type="button" className="landing-cta btn btn-primary" onClick={() => navigate('/plan')}>
          Create trip with us
          <ArrowRight size={18} />
        </button>
      </section>
    </main>
  );
}