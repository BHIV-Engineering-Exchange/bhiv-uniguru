import { Component, ErrorInfo, ReactNode } from "react";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
  errorId: string;
};

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, errorId: "" };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true, errorId: crypto.randomUUID() };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorId = this.state.errorId || crypto.randomUUID();
    console.error("UniGuru frontend error", { errorId, error, componentStack: errorInfo.componentStack });
    window.dispatchEvent(
      new CustomEvent("uniguru:frontend-error", {
        detail: { errorId, message: error.message, componentStack: errorInfo.componentStack },
      }),
    );
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <main role="alert" className="flex min-h-screen items-center justify-center bg-black px-6 text-white">
        <section className="w-full max-w-md rounded-lg border border-red-400/40 bg-slate-950 p-8 text-center shadow-2xl">
          <h1 className="text-2xl font-semibold">UniGuru needs a fresh start</h1>
          <p className="mt-3 text-sm text-slate-300">
            Something unexpected interrupted this page. Your request was not lost.
          </p>
          <button
            type="button"
            onClick={this.handleReload}
            className="mt-6 rounded-md bg-amber-300 px-5 py-3 font-semibold text-slate-950 transition hover:bg-amber-200"
          >
            Reload UniGuru
          </button>
        </section>
      </main>
    );
  }
}