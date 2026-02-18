import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="bg-slate-900 text-white py-24 px-4">
          <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
            <div>
              <span className="inline-block bg-blue-700 text-white text-xs tracking-widest font-semibold px-4 py-2 rounded-full mb-6">
                SMART EXAM ALERTS
              </span>
              {user && (
                <p className="text-blue-300 font-semibold text-lg mb-2">
                  Welcome back, {user.name.split(" ")[0]}! {"\u{1F44B}"}
                </p>
              )}
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
                Never Miss a{" "}
                <span className="text-blue-400">Government Job</span> Deadline
                Again
              </h1>
              <p className="text-lg text-slate-300 mb-8">
                Smart alerts for UPSC, SSC, Banking, and 50+ competitive exams
              </p>
              {user ? (
                <Link
                  to="/dashboard"
                  className="inline-block bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3 rounded-xl shadow-lg transition-colors"
                >
                  Go to Dashboard {" \u2192"}
                </Link>
              ) : (
                <Link
                  to="/register"
                  className="inline-block bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3 rounded-xl shadow-lg transition-colors"
                >
                  Start Free Monitoring
                </Link>
              )}
              <p className="text-slate-300 text-base mt-4">
                Trusted by serious aspirants preparing for competitive exams.
              </p>
            </div>
            <div className="hidden md:flex justify-center">
              <div className="bg-slate-800 border border-slate-700 rounded-2xl p-12 text-center shadow-xl">
                <div className="w-24 h-24 border-4 border-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="white">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
                  </svg>
                </div>
                <p className="text-slate-300 text-base">
                  Get notified only when an opportunity matches your profile and
                  goals.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Problem Section */}
        <section id="about" className="py-20 px-4 bg-white">
          <div className="max-w-7xl mx-auto text-center">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-4">
              Are You Missing Opportunities?
            </h2>
            <p className="text-slate-500 max-w-2xl mx-auto mb-12">
              Government job notifications are scattered across hundreds of
              websites. Missing one deadline can cost you a year of preparation.
            </p>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: "\u{1F4CB}",
                  title: "100+ Websites",
                  desc: "Recruitment notifications scattered across UPSC, SSC, State PSCs, Banks, Railways and more",
                },
                {
                  icon: "\u{23F0}",
                  title: "Daily Manual Check",
                  desc: "Students waste hours manually checking each website every single day",
                },
                {
                  icon: "\u{1F494}",
                  title: "Missed Deadlines",
                  desc: "One missed notification means waiting an entire year for the next exam cycle",
                },
              ].map((item, i) => (
                <div
                  key={i}
                  className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 text-left"
                >
                  <div className="w-14 h-14 bg-slate-100 rounded-xl flex items-center justify-center text-3xl mb-4">
                    {item.icon}
                  </div>
                  <h3 className="font-bold text-slate-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-slate-500 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-20 px-4 bg-slate-50">
          <div className="max-w-7xl mx-auto text-center">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-4">
              How Saspirant Works
            </h2>
            <p className="text-slate-500 max-w-2xl mx-auto mb-12">
              Set it up once. Get alerts forever.
            </p>
            <div className="relative grid md:grid-cols-4 gap-6">
              <div className="hidden md:block absolute left-12 right-12 top-10 h-px bg-slate-200"></div>
              {[
                {
                  step: "1",
                  icon: "\u{1F464}",
                  title: "Create Account",
                  desc: "Sign up with email or Google in seconds",
                },
                {
                  step: "2",
                  icon: "\u2699\uFE0F",
                  title: "Set Preferences",
                  desc: "Choose exam types, age range, and qualification",
                },
                {
                  step: "3",
                  icon: "\u{1F50D}",
                  title: "Add Websites",
                  desc: "Add official recruitment websites to monitor",
                },
                {
                  step: "4",
                  icon: "\u{1F4E7}",
                  title: "Get Alerts",
                  desc: "Receive email alerts for matching opportunities",
                },
              ].map((item, i) => (
                <div key={i} className="relative p-6 text-center">
                  <div className="relative z-10 mx-auto w-9 h-9 bg-blue-700 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {item.step}
                  </div>
                  <div className="mt-4 mb-4 bg-white rounded-xl shadow-sm border border-slate-200 p-4 text-3xl">
                    {item.icon}
                  </div>
                  <h3 className="font-bold text-slate-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-slate-500 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4 bg-white">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-extrabold text-slate-900 mb-4">
                Everything You Need
              </h2>
              <p className="text-slate-500">
                Built specifically for Indian competitive exam aspirants
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  icon: "\u{1F3AF}",
                  title: "Smart Matching",
                  desc: "AI-powered filtering matches jobs to your exact age, qualification, and exam preferences",
                },
                {
                  icon: "\u26A1",
                  title: "24/7 Monitoring",
                  desc: "Automated scraping runs every 6 hours so you never miss a fresh notification",
                },
                {
                  icon: "\u{1F4F1}",
                  title: "Instant Email Alerts",
                  desc: "Get notified immediately when a matching opportunity is posted",
                },
                {
                  icon: "\u{1F512}",
                  title: "Secure Login",
                  desc: "Sign in with Google or email/password with enterprise-grade security",
                },
                {
                  icon: "\u{1F4CA}",
                  title: "Smart Dashboard",
                  desc: "Track all alerts, upcoming deadlines, and monitoring status in one place",
                },
                {
                  icon: "\u{1F193}",
                  title: "100% Free",
                  desc: "No credit card required. Free forever for core features",
                },
              ].map((item, i) => (
                <div
                  key={i}
                  className="border border-slate-100 rounded-2xl p-6 hover:shadow-md transition-shadow"
                >
                  <div className="inline-flex bg-blue-50 rounded-xl p-3 text-3xl mb-3">
                    {item.icon}
                  </div>
                  <h3 className="font-bold text-slate-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-slate-500 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Supported Exams */}
        <section className="py-20 px-4 bg-slate-900">
          <div className="max-w-7xl mx-auto text-center">
            <h2 className="text-3xl font-extrabold text-white mb-4">
              Supported Exam Categories
            </h2>
            <p className="text-slate-300 mb-12">
              We monitor notifications for all major competitive exams
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {[
                "UPSC",
                "SSC",
                "Banking",
                "Railways",
                "State PSC",
                "University",
                "Defence",
                "Teaching",
                "Medical",
                "Engineering",
              ].map((exam, i) => (
                <span
                  key={i}
                  className="bg-blue-800 text-blue-100 border border-blue-700 rounded-full px-5 py-2 font-medium text-sm hover:bg-blue-700 transition-colors"
                >
                  {exam}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4 bg-slate-800 text-white">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-extrabold mb-4">
              Ready to Stay Ahead?
            </h2>
            <p className="text-blue-100 mb-8">
              No credit card required. 100% free for core features.
            </p>
            {user ? (
              <Link
                to="/dashboard"
                className="inline-block bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3 rounded-xl shadow transition-colors"
              >
                Go to Dashboard {" \u2192"}
              </Link>
            ) : (
              <Link
                to="/register"
                className="inline-block bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3 rounded-xl shadow transition-colors"
              >
                Create Free Account
              </Link>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
