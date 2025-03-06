import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex justify-center">
      <SignUp
        routing="hash"
        appearance={{
          elements: {
            formButtonPrimary: 
              "bg-blue-600 hover:bg-blue-700 text-sm normal-case",
            card: "bg-white dark:bg-gray-800 shadow-md",
            headerTitle: "text-gray-900 dark:text-gray-100",
            headerSubtitle: "text-gray-600 dark:text-gray-400",
            formFieldLabel: "text-gray-700 dark:text-gray-300",
            formFieldInput: "border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100",
            footerActionLink: "text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300",
          },
        }}
        signInUrl="/auth/sign-in"
      />
    </div>
  );
}
