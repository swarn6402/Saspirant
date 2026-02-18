import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Terms() {
  return (
    <div className="bg-gray-50 min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
            <h1 className="text-3xl font-extrabold text-gray-900">Terms of Service</h1>
            <p className="text-sm text-gray-500 mt-2">Last updated: February 14, 2026</p>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">1. Service Description</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                Saspirant provides exam and job notification monitoring for competitive exams in India
                and collects public notices from official sources.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">2. User Responsibilities</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                You must provide accurate profile details, keep preferences updated, use the service
                lawfully, and verify final eligibility and deadlines on official websites.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">3. Availability and Free Tier Limits</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                This is an MVP/free-tier service. Availability may vary due to third-party limits,
                and features may pause or change at any time.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">4. No Guarantee of Completeness</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                We aim for high accuracy but do not guarantee completeness. Users must confirm details
                with official authorities before applying.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">5. Limitation of Liability</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                We are not liable for missed deadlines, incorrect third-party data, delivery delays,
                or indirect losses.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">6. Changes to Terms</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                Continued use after updates means acceptance of the updated Terms.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">7. Contact</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                For any questions about these terms, contact us at{' '}
                <a href="mailto:swarnjeettiwary02@gmail.com" className="text-indigo-600 hover:underline">
                  swarnjeettiwary02@gmail.com
                </a>
                .
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
