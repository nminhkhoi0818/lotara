"use client";

import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, Users, Award, Activity } from "lucide-react";

const metrics = [
  {
    icon: Users,
    label: "Total Users",
    value: "2,847",
    change: "+12.5%",
    color: "primary",
  },
  {
    icon: Award,
    label: "Avg Satisfaction",
    value: "8.7/10",
    change: "+2.3%",
    color: "secondary",
  },
  {
    icon: TrendingUp,
    label: "Budget Accuracy",
    value: "94%",
    change: "+3.1%",
    color: "accent",
  },
  {
    icon: Activity,
    label: "Active Trips",
    value: "1,246",
    change: "+18.2%",
    color: "primary",
  },
];

const promptVersionData = [
  { version: "v1.0", score: 7.8, tests: 150 },
  { version: "v1.1", score: 8.1, tests: 200 },
  { version: "v1.2", score: 8.4, tests: 220 },
  { version: "v2.0", score: 8.7, tests: 350 },
  { version: "v2.1", score: 8.9, tests: 400 },
];

const modelComparisonData = [
  { model: "GPT-4", personalization: 8.5, budget: 9.2, satisfaction: 8.8 },
  { model: "Claude", personalization: 8.7, budget: 8.9, satisfaction: 8.9 },
  { model: "Grok", personalization: 8.2, budget: 8.6, satisfaction: 8.4 },
];

const recentRuns = [
  {
    id: "RUN-2847",
    model: "Claude 3.5",
    prompt: "v2.1",
    score: 9.1,
    time: "Just now",
  },
  {
    id: "RUN-2846",
    model: "GPT-4",
    prompt: "v2.0",
    score: 8.9,
    time: "2 mins ago",
  },
  {
    id: "RUN-2845",
    model: "Claude 3.5",
    prompt: "v2.1",
    score: 8.8,
    time: "5 mins ago",
  },
  {
    id: "RUN-2844",
    model: "Grok",
    prompt: "v1.9",
    score: 7.6,
    time: "12 mins ago",
  },
  {
    id: "RUN-2843",
    model: "GPT-4",
    prompt: "v2.0",
    score: 9.2,
    time: "18 mins ago",
  },
];

export default function AdminPage() {
  const colorMap: Record<string, string> = {
    primary: "bg-primary/10 text-primary",
    secondary: "bg-secondary/10 text-secondary",
    accent: "bg-accent/10 text-accent",
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-24">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3">
              Judge Dashboard
            </h1>
            <p className="text-lg text-muted-foreground">
              AI model experimentation & performance metrics
            </p>
          </div>

          {/* Metrics Grid */}
          <div className="grid md:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric, i) => {
              const Icon = metric.icon;
              const colorClass = colorMap[metric.color] || colorMap.primary;
              return (
                <Card key={i} className="p-6 rounded-2xl border-border/50">
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`w-12 h-12 rounded-lg ${colorClass} flex items-center justify-center`}
                    >
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-sm font-semibold text-green-600">
                      {metric.change}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-1">
                    {metric.label}
                  </p>
                  <p className="text-3xl font-bold text-foreground">
                    {metric.value}
                  </p>
                </Card>
              );
            })}
          </div>

          {/* Tabs */}
          <Tabs defaultValue="prompt-versions" className="w-full">
            <TabsList className="grid w-full md:w-auto grid-cols-3 mb-8">
              <TabsTrigger value="prompt-versions">Prompt Versions</TabsTrigger>
              <TabsTrigger value="model-comparison">
                Model Comparison
              </TabsTrigger>
              <TabsTrigger value="recent-runs">Recent Runs</TabsTrigger>
            </TabsList>

            {/* Prompt Versions Chart */}
            <TabsContent value="prompt-versions" className="space-y-6">
              <Card className="p-6 md:p-8 rounded-2xl border-border/50">
                <h3 className="text-xl font-semibold text-foreground mb-6">
                  Prompt Version Performance
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={promptVersionData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="var(--color-border)"
                    />
                    <XAxis
                      dataKey="version"
                      stroke="var(--color-muted-foreground)"
                    />
                    <YAxis stroke="var(--color-muted-foreground)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "var(--color-card)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "8px",
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="var(--color-primary)"
                      strokeWidth={2}
                      name="Avg Score"
                    />
                    <Line
                      type="monotone"
                      dataKey="tests"
                      stroke="var(--color-secondary)"
                      strokeWidth={2}
                      name="Tests Run"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              <div className="grid md:grid-cols-3 gap-6">
                {promptVersionData.slice(-3).map((data, i) => (
                  <Card key={i} className="p-6 rounded-2xl border-border/50">
                    <h4 className="text-lg font-semibold text-foreground mb-4">
                      {data.version}
                    </h4>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">
                          Score
                        </p>
                        <p className="text-2xl font-bold text-primary">
                          {data.score}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">
                          Tests
                        </p>
                        <p className="text-lg font-semibold text-foreground">
                          {data.tests}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Model Comparison */}
            <TabsContent value="model-comparison" className="space-y-6">
              <Card className="p-6 md:p-8 rounded-2xl border-border/50">
                <h3 className="text-xl font-semibold text-foreground mb-6">
                  Model Performance Comparison
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={modelComparisonData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="var(--color-border)"
                    />
                    <XAxis
                      dataKey="model"
                      stroke="var(--color-muted-foreground)"
                    />
                    <YAxis stroke="var(--color-muted-foreground)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "var(--color-card)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "8px",
                      }}
                    />
                    <Legend />
                    <Bar
                      dataKey="personalization"
                      fill="var(--color-primary)"
                      name="Personalization"
                    />
                    <Bar
                      dataKey="budget"
                      fill="var(--color-secondary)"
                      name="Budget Accuracy"
                    />
                    <Bar
                      dataKey="satisfaction"
                      fill="var(--color-accent)"
                      name="Satisfaction"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              <div className="grid md:grid-cols-3 gap-6">
                {modelComparisonData.map((data, i) => (
                  <Card key={i} className="p-6 rounded-2xl border-border/50">
                    <h4 className="text-lg font-semibold text-foreground mb-4">
                      {data.model}
                    </h4>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">
                          Personalization
                        </p>
                        <p className="text-xl font-bold text-primary">
                          {data.personalization}/10
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">
                          Budget Accuracy
                        </p>
                        <p className="text-xl font-bold text-secondary">
                          {data.budget}/10
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">
                          Satisfaction
                        </p>
                        <p className="text-xl font-bold text-accent">
                          {data.satisfaction}/10
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Recent Runs Table */}
            <TabsContent value="recent-runs" className="space-y-6">
              <Card className="p-6 md:p-8 rounded-2xl border-border/50 overflow-x-auto">
                <h3 className="text-xl font-semibold text-foreground mb-6">
                  Recent Experimental Runs
                </h3>
                <div className="min-w-max">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border/50">
                        <th className="text-left py-3 px-4 font-semibold text-foreground">
                          Run ID
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-foreground">
                          Model
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-foreground">
                          Prompt
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-foreground">
                          Score
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-foreground">
                          Timestamp
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentRuns.map((run, i) => (
                        <tr
                          key={i}
                          className="border-b border-border/30 hover:bg-muted/30 transition-colors"
                        >
                          <td className="py-3 px-4 font-mono text-primary">
                            {run.id}
                          </td>
                          <td className="py-3 px-4 text-foreground">
                            {run.model}
                          </td>
                          <td className="py-3 px-4 text-foreground">
                            {run.prompt}
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-3 py-1 rounded-full bg-primary/10 font-semibold text-primary">
                              {run.score}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-muted-foreground">
                            {run.time}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}
