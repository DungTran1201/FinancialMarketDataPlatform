export type AgentWorkflowStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface WorkflowNodeState {
  node_name: 'intake_and_classify' | 'gather_evidence' | 'synthesize_analysis' | 'validate_citations' | 'publish_report';
  status: 'PENDING' | 'ACTIVE' | 'DONE' | 'SKIPPED' | 'FAILED';
  duration_ms?: number;
  output_summary?: string;
}

export interface ProvenanceCitation {
  id: string;
  tool_invoked: string;
  source_table: string;
  query_fingerprint: string;
  rows_examined: number;
  verified: boolean;
}

export interface InvestigationReport {
  report_id: string;
  run_id: string;
  title: string;
  summary: string;
  content_markdown: string;
  citations: ProvenanceCitation[];
  created_at: string;
  author_agent: string;
}

export interface AgentRunTicket {
  run_id: string;
  objective: string;
  triggered_by: 'USER_REST' | 'ANOMALY_DETECTOR';
  status: AgentWorkflowStatus;
  nodes: WorkflowNodeState[];
  current_node?: string;
  report?: InvestigationReport;
  started_at: string;
  completed_at?: string;
}

