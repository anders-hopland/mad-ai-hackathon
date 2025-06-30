"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCreateTestRun } from "@/lib/hooks";
import { LinkIcon, PlayCircleIcon, ChatTextIcon } from "@phosphor-icons/react";

// URL transformer function to prepend https:// if needed
const transformUrl = (url: string): string => {
  if (!url) return url;
  return url.match(/^https?:\/\//) ? url : `https://${url}`;
};

// Form validation schema
const testFormSchema = z.object({
  url: z.string()
    .min(1, "URL is required")
    .transform(transformUrl)
    .pipe(z.string().url("Please enter a valid URL")),
  scenario: z.string().min(10, "Scenario must be at least 10 characters"),
});

type TestFormValues = z.infer<typeof testFormSchema>;

export default function TestForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const createTestRun = useCreateTestRun();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TestFormValues>({
    resolver: zodResolver(testFormSchema),
    defaultValues: {
      url: "",
      scenario: "",
    },
  });

  const onSubmit = async (data: TestFormValues) => {
    setIsSubmitting(true);

    try {
      const result = await createTestRun.mutateAsync({
        url: data.url,
        scenario: data.scenario,
      });

      // Redirect to the test result page
      router.push(`/tests/${result.id}`);
    } catch (error) {
      console.error("Error creating test run:", error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card bg-base-100 shadow-xl border border-base-300">
      <div className="card-body">
        <h2 className="card-title text-2xl mb-6">Start a New Test</h2>

        <form onSubmit={handleSubmit(onSubmit)}>
          <fieldset className="fieldset mb-4">
            <legend className="fieldset-legend">
              <span className="flex items-center gap-2">
                <LinkIcon className="h-4 w-4" weight="duotone" />
                Website URL
              </span>
            </legend>
            <div className="w-full">
              <input
                type="text" 
                placeholder="example.com or https://example.com"
                className={`input input-bordered w-full ${errors.url ? "input-error" : ""}`}
                {...register("url")}
              />
            </div>
            {errors.url && (
              <p className="text-error text-sm mt-1">
                {errors.url.message}
              </p>
            )}
          </fieldset>

          <fieldset className="fieldset mb-6">
            <legend className="fieldset-legend">
              <span className="flex items-center gap-2">
                <ChatTextIcon className="h-4 w-4" weight="duotone" />
                Test Scenario
              </span>
            </legend>
            <textarea
              placeholder="Describe what you want to test..."
              className={`textarea textarea-bordered w-full ${errors.scenario ? "textarea-error" : ""}`}
              {...register("scenario")}
              rows={4}
            />
            {errors.scenario && (
              <p className="text-error text-sm mt-1">
                {errors.scenario.message}
              </p>
            )}
            <p className="text-xs mt-1 text-base-content/70">
              Describe the feature or functionality you want to test in detail.
            </p>
          </fieldset>

          <div className="card-actions justify-end">
            <button
              type="submit"
              className="btn btn-primary btn-lg gap-2"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="loading loading-spinner"></span>
                  Running...
                </>
              ) : (
                <>
                  <PlayCircleIcon className="h-5 w-5" weight="fill" />
                  Run Test
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
