import type { WitnessSummary } from "@/lib/api";

type ParitySummary = {
  case_count: number;
  comparable_count: number;
  passed_count: number;
  failed_count: number;
  missing_witness_count: number;
  not_reviewed_count: number;
  not_comparable_count: number;
  target_reviewed_count: number;
  target_met: boolean;
};

type ParityPayload = {
  available: boolean;
  target_met?: boolean;
  summary?: ParitySummary;
  [key: string]: unknown;
};

type ParityKey =
  | "witness_core_parity"
  | "witness_varga_parity"
  | "witness_dasha_parity"
  | "witness_panchanga_parity"
  | "witness_ashtakavarga_parity"
  | "witness_strengths_parity"
  | "witness_yoga_parity"
  | "witness_special_points_parity"
  | "witness_argala_parity"
  | "witness_avastha_parity"
  | "witness_drishti_parity"
  | "witness_transit_coordinate_parity"
  | "witness_compatibility_parity"
  | "witness_muhurta_parity"
  | "witness_tithi_pravesha_parity"
  | "witness_tajaka_parity"
  | "witness_prashna_parity"
  | "witness_jaimini_karaka_parity"
  | "witness_jaimini_varga_parity";

export type ParityRoadmapState = "ready" | "review" | "waiting";

export type ParityRoadmapRow = {
  key: ParityKey;
  label: string;
  state: ParityRoadmapState;
  passed: number;
  target: number;
  failed: number;
  missing: number;
  skipped: number;
  readinessGaps: number;
  action: "ready for demo" | "review witness rows" | "collect report";
};

export type ParityCollectionChecklistRow = ParityRoadmapRow & {
  collectionHint: string;
};

export type ParityCollectionChecklistTotals = {
  ready: number;
  review: number;
  waiting: number;
};

export type ReleaseGateActionSummary = {
  totals: {
    collectReports: number;
    reviewRows: number;
    readyDemo: number;
  };
  smokeMatrixStatus: "ready";
  smokeMatrixText: "command smoke matrix: ready";
  collectReportRows: ParityCollectionChecklistRow[];
  reviewRows: ParityCollectionChecklistRow[];
  readyRows: ParityCollectionChecklistRow[];
};

export type CollectionPlanSnapshotRunbook = {
  schemaVersion: "witness-parity-collection-plan.v1";
  commandHint: "manage.py build_witness_parity_collection_plan_report --output <report-json>";
  dryRunCopy: "dry-run plan";
  noCollectionCopy: "does not collect or generate reports";
  releaseGateStatus: "blocked" | "ready";
  totals: {
    domainCount: number;
    collectReports: number;
    reviewRows: number;
    readyDemo: number;
  };
};

export type ArtifactAvailabilityCheckpoint = {
  title: "Artifact availability checkpoint";
  environmentCopy: "environment artifact availability";
  localDevCopy: "local dev can show 19/19/0";
  productionCopy: "production can show 19/19/0";
  environmentDetailCopy: "committed artifact availability is aligned; release remains blocked by review witness rows";
  releaseGateStatus: "blocked" | "ready";
  commandSmokeMatrixStatus: "ready";
  commandSmokeMatrixText: "command smoke matrix: ready";
  totals: {
    domainCount: number;
    availableReviewRows: number;
    missingReports: number;
    collectReports: number;
    reviewRows: number;
    readyDemo: number;
  };
};

export type CoreReviewPreflightBlocker = {
  title: "Core review preflight";
  domainKey: "witness_core_parity";
  notReviewedRows: 20;
  sourceFamilyLabel: "source family coverage";
  sourceFamilyCoverage: "both";
  releaseGateStatus: "blocked";
  statusCopy: "release remains blocked";
  detailCopy: "blocked by not-reviewed witness rows";
  safeCommandFamilies: [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
  ];
  cautionCopy: "No acceptance or release readiness is claimed";
};

export type CoreReviewProgress = {
  title: "Core review progress";
  targetCaseId: "sterlitamak-1998-04-30-1345";
  reviewedRows: 1;
  remainingNotReviewedRows: 20;
  comparableRows: 1;
  failedRows: 1;
  maxAbsDeltaArcseconds: 94.064472;
  statusCopy: "real diff; release remains blocked";
  detailCopy: "first reviewed row is comparable and failed";
};

export type CoreReviewBatchScan = {
  title: "Core review batch scan";
  evidenceTitle: "Evidence backlog";
  stage: "P51-A";
  requestedCloseCount: 5;
  scannedCandidates: 20;
  closedRows: 0;
  skippedRows: 20;
  remainingNotReviewedRows: 20;
  firstSkippedCaseId: "vrindavan-1990-08-15-1024";
  lastSkippedCaseId: "mayapur-2026-01-01-0000";
  blockerLabels: ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"];
  statusCopy: "existing review commands found no reviewable rows because evidence/manual values are missing or blocked";
  nextOperatorAction: "collect/attach missing JHora screenshots and Parashara Light evidence/manual values before running mark commands";
  safeCommandFamilies: [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
  ];
  cautionCopy: "No batch row is reviewed or parity-passing from this scan";
};

export type CoreEvidenceBacklog = {
  title: "Core evidence backlog";
  schemaVersion: "jyotish-core-evidence-backlog-v1";
  stage: "P53-A";
  backlogRows: 20;
  blockedRows: 20;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  jhoraEvidenceBacklog: 20;
  parasharaLightEvidenceBacklog: 20;
  requiredEvidenceFamilies: ["jhora_screenshot_or_packet", "parashara_light_manual_values_or_packet"];
  firstBacklogCaseId: "vrindavan-1990-08-15-1024";
  lastBacklogCaseId: "mayapur-2026-01-01-0000";
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  nextActions: [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_preflight_witness_review",
  ];
  safeCommandFamilies: [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
  ];
  statusCopy: "evidence backlog is blocking mark commands";
  cautionCopy: "No evidence availability, parity pass, or release readiness is claimed";
};

export type CoreEvidenceIntakePlan = {
  title: "Core evidence intake plan";
  schemaVersion: "jyotish-core-evidence-intake-plan-v1";
  stage: "P55-A";
  intakeRows: 5;
  readyToMarkRows: 0;
  evidenceFilesCommitted: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  evidenceSlotStatus: {
    jhora_screenshot_or_packet: "missing";
    parashara_light_manual_values_or_packet: "missing";
  };
  safeNextActions: [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_preflight_witness_review",
  ];
  safeValidationCommandFamilies: [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
  ];
  statusCopy: "first evidence intake batch is blocked until evidence is collected";
  cautionCopy: "No mark command should run until evidence is collected/attached";
};

export type CoreEvidenceReadiness = {
  title: "Core evidence readiness";
  schemaVersion: "jyotish-core-evidence-readiness-preflight-v1";
  stage: "P57-A";
  readinessRows: 5;
  operatorPacketRows: 5;
  readyToMarkRows: 0;
  blockedRows: 5;
  missingEvidenceSlots: 10;
  jhoraMissingCount: 5;
  parasharaLightMissingCount: 5;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  evidenceSlotStatus: {
    jhora_screenshot_or_packet: "missing";
    parashara_light_manual_values_or_packet: "missing";
  };
  readinessStatus: "blocked_missing_evidence";
  readyToMarkLabel: "ready_to_mark=false";
  safeNextActions: [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_preflight_witness_review",
  ];
  safeValidationCommandFamilies: [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
  ];
  operatorNote: "Evidence must be collected and attached before mark commands are attempted";
  statusCopy: "external evidence is missing for every selected intake row";
  cautionCopy: "No parity pass or release readiness is claimed";
};

export type CoreEvidencePipeline = {
  title: "Core evidence pipeline";
  latestStage: "P75-A";
  stageSequence: [
    "P53 backlog",
    "P55 intake",
    "P57 readiness",
    "P59 attachment gate",
    "P61 work orders",
    "P63 handoff",
    "P65 operator packets",
    "P67 QA preflight",
    "P69 attachment readiness",
    "P71 external intake contract",
    "P73 external receipt gate",
    "P75 receipt manifest templates",
  ];
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  backlogSummary: {
    blockedRows: 20;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  intakeSummary: {
    intakeRows: 5;
    readyToMarkRows: 0;
    evidenceFilesCommitted: 0;
    remainingNotReviewedRows: 20;
  };
  readinessSummary: {
    readinessRows: 5;
    operatorPacketRows: 5;
    readyToMarkRows: 0;
    blockedRows: 5;
    missingEvidenceSlots: 10;
    jhoraMissingCount: 5;
    parasharaLightMissingCount: 5;
    remainingNotReviewedRows: 20;
  };
  attachmentSummary: {
    attachmentRows: 5;
    operatorAttachmentManifestRows: 5;
    readyToMarkRows: 0;
    blockedRows: 5;
    missingAttachmentSlots: 10;
    attachedEvidenceFiles: 0;
    attachedEvidenceFamilyCount: 0;
    jhoraAttachedCount: 0;
    parasharaLightAttachedCount: 0;
    jhoraMissingCount: 5;
    parasharaLightMissingCount: 5;
    remainingNotReviewedRows: 20;
  };
  workOrderSummary: {
    workOrderRows: 10;
    pendingWorkOrderCount: 10;
    pendingJhoraWorkOrderCount: 5;
    pendingParasharaLightWorkOrderCount: 5;
    blockedCaseCount: 5;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  handoffSummary: {
    caseHandoffRows: 5;
    handoffWorkOrderRows: 10;
    pendingHandoffCount: 10;
    pendingJhoraHandoffCount: 5;
    pendingParasharaLightHandoffCount: 5;
    blockedCaseCount: 5;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  operatorPacketSummary: {
    operatorPacketRows: 5;
    operatorAttachmentSlotRows: 10;
    pendingOperatorPacketCount: 5;
    pendingOperatorAttachmentSlotCount: 10;
    pendingJhoraAttachmentSlotCount: 5;
    pendingParasharaLightAttachmentSlotCount: 5;
    blockedPacketCount: 5;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  operatorPacketQaSummary: {
    operatorPacketQaRows: 5;
    attachmentSlotQaRows: 10;
    blockedPacketQaCount: 5;
    pendingAttachmentSlotQaCount: 10;
    pendingJhoraAttachmentSlotQaCount: 5;
    pendingParasharaLightAttachmentSlotQaCount: 5;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  attachmentReadinessSummary: {
    caseAttachmentReadinessRows: 5;
    attachmentReadinessSlotRows: 10;
    blockedCaseAttachmentCount: 5;
    pendingExternalEvidenceAttachmentCount: 10;
    pendingJhoraExternalAttachmentCount: 5;
    pendingParasharaLightExternalAttachmentCount: 5;
    readyToAttachRows: 0;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  externalIntakeSummary: {
    caseIntakeContractRows: 5;
    attachmentIntakeSlotRows: 10;
    pendingExternalEvidenceIntakeCount: 10;
    pendingJhoraExternalIntakeCount: 5;
    pendingParasharaLightExternalIntakeCount: 5;
    evidenceCollectedCount: 0;
    evidenceUploadedCount: 0;
    evidenceAttachedCount: 0;
    readyToAttachRows: 0;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  externalReceiptSummary: {
    caseReceiptGateRows: 5;
    attachmentReceiptSlotRows: 10;
    pendingExternalEvidenceReceiptCount: 10;
    pendingJhoraReceiptCount: 5;
    pendingParasharaLightReceiptCount: 5;
    evidenceReceivedCount: 0;
    evidenceValidatedCount: 0;
    evidenceUploadedCount: 0;
    evidenceAttachedCount: 0;
    readyToAttachRows: 0;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  externalReceiptManifestSummary: {
    caseReceiptManifestTemplateRows: 5;
    attachmentReceiptManifestTemplateRows: 10;
    pendingExternalEvidenceReceiptManifestCount: 10;
    pendingJhoraReceiptManifestCount: 5;
    pendingParasharaLightReceiptManifestCount: 5;
    receiptManifestReceivedCount: 0;
    evidenceReceivedCount: 0;
    evidenceValidatedCount: 0;
    evidenceFileRecordedCount: 0;
    evidenceHashRecordedCount: 0;
    evidenceUploadedCount: 0;
    evidenceAttachedCount: 0;
    readyToAttachRows: 0;
    readyToMarkRows: 0;
    remainingNotReviewedRows: 20;
  };
  operatorNote: "Evidence must be collected and attached before mark commands are attempted";
  statusCopy: "blocked external evidence receipt manifest template labels";
};

export type CoreEvidenceAttachmentGate = {
  title: "Core evidence attachment gate";
  schemaVersion: "jyotish-core-evidence-attachment-gate-v1";
  stage: "P59-A";
  attachmentRows: 5;
  operatorAttachmentManifestRows: 5;
  readyToMarkRows: 0;
  blockedRows: 5;
  missingAttachmentSlots: 10;
  attachedEvidenceFiles: 0;
  attachedEvidenceFamilyCount: 0;
  jhoraAttachedCount: 0;
  parasharaLightAttachedCount: 0;
  jhoraMissingCount: 5;
  parasharaLightMissingCount: 5;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  p57EvidenceSlotStatus: {
    jhora_screenshot_or_packet: "missing";
    parashara_light_manual_values_or_packet: "missing";
  };
  attachmentSlotStatus: {
    jhora_screenshot_or_packet: "not_attached";
    parashara_light_manual_values_or_packet: "not_attached";
  };
  readinessStatus: "blocked_missing_evidence";
  attachmentGateStatus: "blocked_no_attached_evidence";
  readyToMarkLabel: "ready_to_mark=false";
  safeNextActions: [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_evidence_attachment_gate",
    "rerun_preflight_witness_review",
  ];
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
  ];
  operatorNote: "Evidence must be attached before mark commands are attempted";
  statusCopy: "external evidence is not attached for every selected intake row";
  cautionCopy: "No mark command should run until evidence is attached";
};

export type CoreEvidenceAttachmentWorkOrders = {
  title: "Core evidence attachment work orders";
  schemaVersion: "jyotish-core-evidence-attachment-work-orders-v1";
  stage: "P61-A";
  workOrderRows: 10;
  pendingWorkOrderCount: 10;
  pendingJhoraWorkOrderCount: 5;
  pendingParasharaLightWorkOrderCount: 5;
  blockedCaseCount: 5;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  workOrderStatus: "pending_not_attached";
  caseWorkOrderStatus: "blocked_pending_attachments";
  readyToMarkLabel: "ready_to_mark=false";
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "Evidence must be attached before mark commands are attempted; work orders are labels only and do not collect evidence";
  statusCopy: "work orders remain pending because evidence is not attached";
  cautionCopy: "No work order attaches evidence or permits mark commands";
};

export type CoreEvidenceAttachmentHandoff = {
  title: "Core evidence attachment handoff";
  schemaVersion: "jyotish-core-evidence-attachment-handoff-v1";
  stage: "P63-A";
  caseHandoffRows: 5;
  handoffWorkOrderRows: 10;
  pendingHandoffCount: 10;
  pendingJhoraHandoffCount: 5;
  pendingParasharaLightHandoffCount: 5;
  blockedCaseCount: 5;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  handoffStatus: "blocked_pending_operator_evidence";
  caseWorkOrderStatus: "blocked_pending_attachments";
  readyToMarkLabel: "ready_to_mark=false";
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "external evidence has not been attached; handoff rows are labels only and do not collect evidence";
  statusCopy: "handoff bundle remains blocked pending operator evidence";
  cautionCopy: "No evidence is attached and no release readiness is claimed";
};

export type CoreEvidenceOperatorPackets = {
  title: "Core evidence operator packets";
  schemaVersion: "jyotish-core-evidence-operator-packets-v1";
  stage: "P65-A";
  operatorPacketRows: 5;
  operatorAttachmentSlotRows: 10;
  pendingOperatorPacketCount: 5;
  pendingOperatorAttachmentSlotCount: 10;
  pendingJhoraAttachmentSlotCount: 5;
  pendingParasharaLightAttachmentSlotCount: 5;
  blockedPacketCount: 5;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  packetStatus: "blocked_pending_operator_packet_evidence";
  handoffStatus: "blocked_pending_operator_evidence";
  caseWorkOrderStatus: "blocked_pending_attachments";
  evidenceFileStatus: "not_attached";
  readyToMarkLabel: "ready_to_mark=false";
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_operator_packets_report",
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "external evidence has not been attached; operator packets are labels only and do not collect or attach evidence";
  statusCopy: "operator packet manifest remains blocked pending evidence attachment";
  cautionCopy: "No evidence is attached and no release readiness is claimed";
};

export type CoreEvidenceOperatorPacketQa = {
  title: "Core evidence operator packet QA";
  schemaVersion: "jyotish-core-evidence-operator-packet-qa-v1";
  stage: "P67-A";
  operatorPacketQaRows: 5;
  attachmentSlotQaRows: 10;
  blockedPacketQaCount: 5;
  pendingAttachmentSlotQaCount: 10;
  pendingJhoraAttachmentSlotQaCount: 5;
  pendingParasharaLightAttachmentSlotQaCount: 5;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  qaStatus: "blocked_pending_operator_packet_qa";
  packetStatus: "blocked_pending_operator_packet_evidence";
  attachmentSlotStatus: "not_attached";
  readyToMarkLabel: "ready_to_mark=false";
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_operator_packet_qa_report",
    "build_witness_core_evidence_operator_packets_report",
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "external evidence has not been attached; operator packets are labels only; mark commands remain blocked";
  statusCopy: "QA preflight remains blocked pending operator packet evidence";
  cautionCopy: "No evidence is attached and no release readiness is claimed";
};

export type CoreEvidenceOperatorPacketAttachmentReadiness = {
  title: "Core evidence operator packet attachment readiness";
  schemaVersion: "jyotish-core-evidence-operator-packet-attachment-readiness-v1";
  stage: "P69-A";
  caseAttachmentReadinessRows: 5;
  attachmentReadinessSlotRows: 10;
  blockedCaseAttachmentCount: 5;
  pendingExternalEvidenceAttachmentCount: 10;
  pendingJhoraExternalAttachmentCount: 5;
  pendingParasharaLightExternalAttachmentCount: 5;
  readyToAttachRows: 0;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  slotFamilies: [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
  ];
  readinessStatus: "blocked_pending_external_evidence_attachment";
  qaStatus: "blocked_pending_operator_packet_qa";
  packetStatus: "blocked_pending_operator_packet_evidence";
  attachmentSlotStatus: "not_attached";
  readyToAttachLabel: "ready_to_attach=false";
  readyToMarkLabel: "ready_to_mark=false";
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_operator_packet_qa_report",
    "build_witness_core_evidence_operator_packets_report",
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "external evidence has not been attached; readiness rows are labels only; collection/upload/mark commands are not executed";
  statusCopy: "attachment-readiness labels exist while external evidence remains not attached";
  cautionCopy: "ready-to-attach is false; ready-to-mark is false; release remains blocked";
};

export type CoreEvidenceExternalIntakeContract = {
  title: "Core evidence external intake contract";
  schemaVersion: "jyotish-core-evidence-external-intake-contract-v1";
  stage: "P71-A";
  caseIntakeContractRows: 5;
  attachmentIntakeSlotRows: 10;
  pendingExternalEvidenceIntakeCount: 10;
  pendingJhoraExternalIntakeCount: 5;
  pendingParasharaLightExternalIntakeCount: 5;
  evidenceCollectedCount: 0;
  evidenceUploadedCount: 0;
  evidenceAttachedCount: 0;
  readyToAttachRows: 0;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  slotFamilies: [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
  ];
  intakeStatus: "blocked_pending_external_evidence_intake";
  readinessStatus: "blocked_pending_external_evidence_attachment";
  qaStatus: "blocked_pending_operator_packet_qa";
  packetStatus: "blocked_pending_operator_packet_evidence";
  evidenceFileStatus: "not_attached";
  evidenceCollectionStatus: "not_started";
  evidenceUploadStatus: "not_started";
  evidenceAttachmentStatus: "not_attached";
  readyToAttachLabel: "ready_to_attach=false";
  readyToMarkLabel: "ready_to_mark=false";
  evidenceCollectedLabel: "evidence_collected=false";
  evidenceUploadedLabel: "evidence_uploaded=false";
  evidenceAttachedLabel: "evidence_attached=false";
  safeIntakeLabels: [
    "request_jhora_screenshot_or_packet",
    "request_parashara_light_manual_values_or_packet",
    "receive_external_evidence_from_human",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_operator_packet_qa_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
  ];
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_operator_packet_qa_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "external evidence has not been collected, uploaded, or attached; intake rows are labels only; mark commands are not executed";
  statusCopy: "human-provided external evidence intake is requested as labels only";
  cautionCopy: "nothing is collected, uploaded, or attached; ready-to-attach is false; ready-to-mark is false; release remains blocked";
};

export type CoreEvidenceExternalReceiptGate = {
  title: "Core evidence external receipt gate";
  schemaVersion: "jyotish-core-evidence-external-receipt-gate-v1";
  stage: "P73-A";
  caseReceiptGateRows: 5;
  attachmentReceiptSlotRows: 10;
  pendingExternalEvidenceReceiptCount: 10;
  pendingJhoraReceiptCount: 5;
  pendingParasharaLightReceiptCount: 5;
  evidenceReceivedCount: 0;
  evidenceValidatedCount: 0;
  evidenceUploadedCount: 0;
  evidenceAttachedCount: 0;
  readyToAttachRows: 0;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  paritySuccessClaimed: false;
  releaseReadyClaimed: false;
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  slotFamilies: [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
  ];
  receiptGateStatus: "blocked_pending_external_evidence_receipts";
  intakeStatus: "blocked_pending_external_evidence_intake";
  readinessStatus: "blocked_pending_external_evidence_attachment";
  evidenceReceiptStatus: "not_received";
  evidenceValidationStatus: "not_started";
  evidenceFileStatus: "not_attached";
  evidenceUploadStatus: "not_started";
  evidenceAttachmentStatus: "not_attached";
  readyToAttachLabel: "ready_to_attach=false";
  readyToMarkLabel: "ready_to_mark=false";
  evidenceReceivedLabel: "evidence_received_count=0";
  evidenceValidatedLabel: "evidence_validated_count=0";
  evidenceUploadedLabel: "evidence_uploaded_count=0";
  evidenceAttachedLabel: "evidence_attached_count=0";
  paritySuccessClaimedLabel: "parity_success_claimed=false";
  releaseReadyClaimedLabel: "release_ready_claimed=false";
  safeReceiptLabels: [
    "await_jhora_screenshot_or_packet_receipt",
    "await_parashara_light_manual_values_or_packet_receipt",
    "record_external_evidence_receipt_manifest",
    "rerun_external_receipt_gate_report",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
  ];
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_external_receipt_gate_report",
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "external evidence receipts have not been received or validated; receipt rows are labels only; collection/upload/attachment/mark commands are not executed";
  statusCopy: "external evidence receipt gate remains blocked";
  cautionCopy: "nothing is received, validated, uploaded, or attached; ready-to-attach is false; ready-to-mark is false; release remains blocked";
};

export type CoreEvidenceExternalReceiptManifestTemplates = {
  title: "Core evidence external receipt manifest templates";
  schemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1";
  stage: "P75-A";
  caseReceiptManifestTemplateRows: 5;
  attachmentReceiptManifestTemplateRows: 10;
  pendingExternalEvidenceReceiptManifestCount: 10;
  pendingJhoraReceiptManifestCount: 5;
  pendingParasharaLightReceiptManifestCount: 5;
  receiptManifestReceivedCount: 0;
  evidenceReceivedCount: 0;
  evidenceValidatedCount: 0;
  evidenceFileRecordedCount: 0;
  evidenceHashRecordedCount: 0;
  evidenceUploadedCount: 0;
  evidenceAttachedCount: 0;
  readyToAttachRows: 0;
  readyToMarkRows: 0;
  remainingNotReviewedRows: 20;
  releaseGateStatus: "blocked";
  commandSmokeMatrixStatus: "ready";
  paritySuccessClaimed: false;
  releaseReadyClaimed: false;
  selectedCaseIds: [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
  ];
  slotFamilies: [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
  ];
  receiptManifestTemplateStatus: "blocked_pending_external_evidence_receipt_manifests";
  receiptGateStatus: "blocked_pending_external_evidence_receipts";
  intakeStatus: "blocked_pending_external_evidence_intake";
  readinessStatus: "blocked_pending_external_evidence_attachment";
  receiptManifestStatus: "not_received";
  evidenceValidationStatus: "not_started";
  evidenceFileStatus: "not_attached";
  evidenceHashStatus: "not_recorded";
  evidenceUploadStatus: "not_started";
  evidenceAttachmentStatus: "not_attached";
  readyToAttachLabel: "ready_to_attach=false";
  readyToMarkLabel: "ready_to_mark=false";
  receiptManifestReceivedLabel: "receipt_manifest_received_count=0";
  evidenceReceivedLabel: "evidence_received_count=0";
  evidenceValidatedLabel: "evidence_validated_count=0";
  evidenceFileRecordedLabel: "evidence_file_recorded_count=0";
  evidenceHashRecordedLabel: "evidence_hash_recorded_count=0";
  evidenceUploadedLabel: "evidence_uploaded_count=0";
  evidenceAttachedLabel: "evidence_attached_count=0";
  paritySuccessClaimedLabel: "parity_success_claimed=false";
  releaseReadyClaimedLabel: "release_ready_claimed=false";
  safeManifestTemplateLabels: [
    "await_jhora_receipt_manifest",
    "await_parashara_light_receipt_manifest",
    "record_external_evidence_receipt_manifest",
    "rerun_external_receipt_manifest_templates_report",
    "rerun_external_receipt_gate_report",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
  ];
  safeRequiredManifestFields: [
    "case_id",
    "evidence_family",
    "external_tool_label",
    "human_receipt_timestamp_utc",
    "redacted_receipt_manifest_id",
    "operator_receipt_note_label",
    "no_raw_values_in_manifest",
    "no_private_paths_in_manifest",
    "no_secrets_in_manifest",
  ];
  safeValidationCommandFamilies: [
    "build_witness_core_evidence_external_receipt_manifest_templates_report",
    "build_witness_core_evidence_external_receipt_gate_report",
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
  ];
  operatorNote: "receipt manifests have not arrived; template rows are labels only; no evidence file, hash, upload, attachment, or mark command is executed";
  statusCopy: "external evidence receipt manifest templates remain blocked";
  cautionCopy: "no manifest, evidence, file, hash, upload, attachment, or mark command has happened; ready-to-attach is false; ready-to-mark is false; release remains blocked";
};

export const parityRoadmapItems: Array<{ key: ParityKey; label: string }> = [
  { key: "witness_core_parity", label: "Core parity" },
  { key: "witness_varga_parity", label: "Varga parity" },
  { key: "witness_dasha_parity", label: "Dasha parity" },
  { key: "witness_panchanga_parity", label: "Panchanga parity" },
  { key: "witness_ashtakavarga_parity", label: "Ashtakavarga parity" },
  { key: "witness_strengths_parity", label: "Strengths parity" },
  { key: "witness_yoga_parity", label: "Yoga parity" },
  { key: "witness_special_points_parity", label: "Special points parity" },
  { key: "witness_argala_parity", label: "Argala parity" },
  { key: "witness_avastha_parity", label: "Avastha parity" },
  { key: "witness_drishti_parity", label: "Drishti parity" },
  { key: "witness_transit_coordinate_parity", label: "Transit coordinate parity" },
  { key: "witness_compatibility_parity", label: "Compatibility parity" },
  { key: "witness_muhurta_parity", label: "Muhurta parity" },
  { key: "witness_tithi_pravesha_parity", label: "Tithi Pravesha parity" },
  { key: "witness_tajaka_parity", label: "Tajaka parity" },
  { key: "witness_prashna_parity", label: "Prashna parity" },
  { key: "witness_jaimini_karaka_parity", label: "Jaimini karaka parity" },
  { key: "witness_jaimini_varga_parity", label: "Jaimini varga parity" },
];

const parityCollectionCommandByKey: Record<ParityKey, string> = {
  witness_core_parity: "build_witness_core_parity_report",
  witness_varga_parity: "build_witness_varga_parity_report",
  witness_dasha_parity: "build_witness_dasha_parity_report",
  witness_panchanga_parity: "build_witness_panchanga_parity_report",
  witness_ashtakavarga_parity: "build_witness_ashtakavarga_parity_report",
  witness_strengths_parity: "build_witness_strengths_parity_report",
  witness_yoga_parity: "build_witness_yoga_parity_report",
  witness_special_points_parity: "build_witness_special_points_parity_report",
  witness_argala_parity: "build_witness_argala_parity_report",
  witness_avastha_parity: "build_witness_avastha_parity_report",
  witness_drishti_parity: "build_witness_drishti_parity_report",
  witness_transit_coordinate_parity: "build_witness_transit_coordinates_parity_report",
  witness_compatibility_parity: "build_witness_compatibility_parity_report",
  witness_muhurta_parity: "build_witness_muhurta_parity_report",
  witness_tithi_pravesha_parity: "build_witness_tithi_pravesha_parity_report",
  witness_tajaka_parity: "build_witness_tajaka_parity_report",
  witness_prashna_parity: "build_witness_prashna_parity_report",
  witness_jaimini_karaka_parity: "build_witness_jaimini_karaka_parity_report",
  witness_jaimini_varga_parity: "build_witness_jaimini_varga_parity_report",
};

export function buildParityRoadmapRows(witnessSummary: WitnessSummary | null): ParityRoadmapRow[] {
  return parityRoadmapItems.map((item) => {
    const payload = witnessSummary?.[item.key] as ParityPayload | undefined;
    const summary = payload?.summary;
    const passed = safeNumber(summary?.passed_count);
    const target = safeNumber(summary?.target_reviewed_count);
    const failed = safeNumber(summary?.failed_count);
    const missing =
      safeNumber(summary?.missing_witness_count) +
      safeNumber(summary?.not_reviewed_count) +
      safeNumber(summary?.not_comparable_count);
    const skipped = payload ? skippedCount(payload) : 0;
    const readinessGaps = payload ? readinessGapCount(payload) : 0;
    const targetMet = Boolean(payload?.target_met ?? summary?.target_met);
    const ready = Boolean(payload?.available) && targetMet && failed === 0 && missing === 0;
    const state: ParityRoadmapState = payload?.available ? (ready ? "ready" : "review") : "waiting";

    return {
      key: item.key,
      label: item.label,
      state,
      passed,
      target,
      failed,
      missing,
      skipped,
      readinessGaps,
      action: state === "ready" ? "ready for demo" : state === "review" ? "review witness rows" : "collect report",
    };
  });
}

export function buildParityCollectionChecklistRows(rows: ParityRoadmapRow[]): ParityCollectionChecklistRow[] {
  return rows.map((row) => ({
    ...row,
    collectionHint: `manage.py ${parityCollectionCommandByKey[row.key]} --output <report-json>`,
  }));
}

export function buildParityCollectionChecklistTotals(rows: ParityRoadmapRow[]): ParityCollectionChecklistTotals {
  return rows.reduce<ParityCollectionChecklistTotals>(
    (totals, row) => ({
      ...totals,
      [row.state]: totals[row.state] + 1,
    }),
    { ready: 0, review: 0, waiting: 0 },
  );
}

export function buildReleaseGateActionSummary(rows: ParityCollectionChecklistRow[]): ReleaseGateActionSummary {
  const collectReportRows = rows.filter((row) => row.action === "collect report");
  const reviewRows = rows.filter((row) => row.action === "review witness rows");
  const readyRows = rows.filter((row) => row.action === "ready for demo");
  return {
    totals: {
      collectReports: collectReportRows.length,
      reviewRows: reviewRows.length,
      readyDemo: readyRows.length,
    },
    smokeMatrixStatus: "ready",
    smokeMatrixText: "command smoke matrix: ready",
    collectReportRows,
    reviewRows,
    readyRows,
  };
}

export function buildCollectionPlanSnapshotRunbook(
  rows: ParityCollectionChecklistRow[],
  releaseGateActionSummary: ReleaseGateActionSummary,
): CollectionPlanSnapshotRunbook {
  const blocked = releaseGateActionSummary.totals.collectReports > 0 || releaseGateActionSummary.totals.reviewRows > 0;
  return {
    schemaVersion: "witness-parity-collection-plan.v1",
    commandHint: "manage.py build_witness_parity_collection_plan_report --output <report-json>",
    dryRunCopy: "dry-run plan",
    noCollectionCopy: "does not collect or generate reports",
    releaseGateStatus: blocked ? "blocked" : "ready",
    totals: {
      domainCount: rows.length,
      collectReports: releaseGateActionSummary.totals.collectReports,
      reviewRows: releaseGateActionSummary.totals.reviewRows,
      readyDemo: releaseGateActionSummary.totals.readyDemo,
    },
  };
}

export function buildArtifactAvailabilityCheckpoint(
  rows: ParityCollectionChecklistRow[],
  releaseGateActionSummary: ReleaseGateActionSummary,
): ArtifactAvailabilityCheckpoint {
  const missingReports = releaseGateActionSummary.totals.collectReports;
  const blocked = missingReports > 0 || releaseGateActionSummary.totals.reviewRows > 0;
  return {
    title: "Artifact availability checkpoint",
    environmentCopy: "environment artifact availability",
    localDevCopy: "local dev can show 19/19/0",
    productionCopy: "production can show 19/19/0",
    environmentDetailCopy: "committed artifact availability is aligned; release remains blocked by review witness rows",
    releaseGateStatus: blocked ? "blocked" : "ready",
    commandSmokeMatrixStatus: "ready",
    commandSmokeMatrixText: "command smoke matrix: ready",
    totals: {
      domainCount: rows.length,
      availableReviewRows: rows.length - missingReports,
      missingReports,
      collectReports: missingReports,
      reviewRows: releaseGateActionSummary.totals.reviewRows,
      readyDemo: releaseGateActionSummary.totals.readyDemo,
    },
  };
}

export function buildCoreReviewPreflightBlocker(): CoreReviewPreflightBlocker {
  return {
    title: "Core review preflight",
    domainKey: "witness_core_parity",
    notReviewedRows: 20,
    sourceFamilyLabel: "source family coverage",
    sourceFamilyCoverage: "both",
    releaseGateStatus: "blocked",
    statusCopy: "release remains blocked",
    detailCopy: "blocked by not-reviewed witness rows",
    safeCommandFamilies: [
      "preflight_witness_review",
      "mark_jhora_witness_reviewed",
      "mark_parashara_light_witness_reviewed",
    ],
    cautionCopy: "No acceptance or release readiness is claimed",
  };
}

export function buildCoreReviewProgress(): CoreReviewProgress {
  return {
    title: "Core review progress",
    targetCaseId: "sterlitamak-1998-04-30-1345",
    reviewedRows: 1,
    remainingNotReviewedRows: 20,
    comparableRows: 1,
    failedRows: 1,
    maxAbsDeltaArcseconds: 94.064472,
    statusCopy: "real diff; release remains blocked",
    detailCopy: "first reviewed row is comparable and failed",
  };
}

export function buildCoreReviewBatchScan(): CoreReviewBatchScan {
  return {
    title: "Core review batch scan",
    evidenceTitle: "Evidence backlog",
    stage: "P51-A",
    requestedCloseCount: 5,
    scannedCandidates: 20,
    closedRows: 0,
    skippedRows: 20,
    remainingNotReviewedRows: 20,
    firstSkippedCaseId: "vrindavan-1990-08-15-1024",
    lastSkippedCaseId: "mayapur-2026-01-01-0000",
    blockerLabels: ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"],
    statusCopy: "existing review commands found no reviewable rows because evidence/manual values are missing or blocked",
    nextOperatorAction: "collect/attach missing JHora screenshots and Parashara Light evidence/manual values before running mark commands",
    safeCommandFamilies: [
      "preflight_witness_review",
      "mark_jhora_witness_reviewed",
      "mark_parashara_light_witness_reviewed",
    ],
    cautionCopy: "No batch row is reviewed or parity-passing from this scan",
  };
}

export function buildCoreEvidenceBacklog(): CoreEvidenceBacklog {
  return {
    title: "Core evidence backlog",
    schemaVersion: "jyotish-core-evidence-backlog-v1",
    stage: "P53-A",
    backlogRows: 20,
    blockedRows: 20,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    jhoraEvidenceBacklog: 20,
    parasharaLightEvidenceBacklog: 20,
    requiredEvidenceFamilies: ["jhora_screenshot_or_packet", "parashara_light_manual_values_or_packet"],
    firstBacklogCaseId: "vrindavan-1990-08-15-1024",
    lastBacklogCaseId: "mayapur-2026-01-01-0000",
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    nextActions: [
      "collect_jhora_screenshot",
      "attach_parashara_light_manual_values",
      "rerun_preflight_witness_review",
    ],
    safeCommandFamilies: [
      "preflight_witness_review",
      "mark_jhora_witness_reviewed",
      "mark_parashara_light_witness_reviewed",
    ],
    statusCopy: "evidence backlog is blocking mark commands",
    cautionCopy: "No evidence availability, parity pass, or release readiness is claimed",
  };
}

export function buildCoreEvidenceIntakePlan(): CoreEvidenceIntakePlan {
  return {
    title: "Core evidence intake plan",
    schemaVersion: "jyotish-core-evidence-intake-plan-v1",
    stage: "P55-A",
    intakeRows: 5,
    readyToMarkRows: 0,
    evidenceFilesCommitted: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    evidenceSlotStatus: {
      jhora_screenshot_or_packet: "missing",
      parashara_light_manual_values_or_packet: "missing",
    },
    safeNextActions: [
      "collect_jhora_screenshot",
      "attach_parashara_light_manual_values",
      "rerun_preflight_witness_review",
    ],
    safeValidationCommandFamilies: [
      "preflight_witness_review",
      "mark_jhora_witness_reviewed",
      "mark_parashara_light_witness_reviewed",
    ],
    statusCopy: "first evidence intake batch is blocked until evidence is collected",
    cautionCopy: "No mark command should run until evidence is collected/attached",
  };
}

export function buildCoreEvidenceReadiness(): CoreEvidenceReadiness {
  return {
    title: "Core evidence readiness",
    schemaVersion: "jyotish-core-evidence-readiness-preflight-v1",
    stage: "P57-A",
    readinessRows: 5,
    operatorPacketRows: 5,
    readyToMarkRows: 0,
    blockedRows: 5,
    missingEvidenceSlots: 10,
    jhoraMissingCount: 5,
    parasharaLightMissingCount: 5,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    evidenceSlotStatus: {
      jhora_screenshot_or_packet: "missing",
      parashara_light_manual_values_or_packet: "missing",
    },
    readinessStatus: "blocked_missing_evidence",
    readyToMarkLabel: "ready_to_mark=false",
    safeNextActions: [
      "collect_jhora_screenshot",
      "attach_parashara_light_manual_values",
      "rerun_preflight_witness_review",
    ],
    safeValidationCommandFamilies: [
      "preflight_witness_review",
      "mark_jhora_witness_reviewed",
      "mark_parashara_light_witness_reviewed",
    ],
    operatorNote: "Evidence must be collected and attached before mark commands are attempted",
    statusCopy: "external evidence is missing for every selected intake row",
    cautionCopy: "No parity pass or release readiness is claimed",
  };
}

export function buildCoreEvidencePipeline(): CoreEvidencePipeline {
  return {
    title: "Core evidence pipeline",
    latestStage: "P75-A",
    stageSequence: [
      "P53 backlog",
      "P55 intake",
      "P57 readiness",
      "P59 attachment gate",
      "P61 work orders",
      "P63 handoff",
      "P65 operator packets",
      "P67 QA preflight",
      "P69 attachment readiness",
      "P71 external intake contract",
      "P73 external receipt gate",
      "P75 receipt manifest templates",
    ],
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    backlogSummary: {
      blockedRows: 20,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    intakeSummary: {
      intakeRows: 5,
      readyToMarkRows: 0,
      evidenceFilesCommitted: 0,
      remainingNotReviewedRows: 20,
    },
    readinessSummary: {
      readinessRows: 5,
      operatorPacketRows: 5,
      readyToMarkRows: 0,
      blockedRows: 5,
      missingEvidenceSlots: 10,
      jhoraMissingCount: 5,
      parasharaLightMissingCount: 5,
      remainingNotReviewedRows: 20,
    },
    attachmentSummary: {
      attachmentRows: 5,
      operatorAttachmentManifestRows: 5,
      readyToMarkRows: 0,
      blockedRows: 5,
      missingAttachmentSlots: 10,
      attachedEvidenceFiles: 0,
      attachedEvidenceFamilyCount: 0,
      jhoraAttachedCount: 0,
      parasharaLightAttachedCount: 0,
      jhoraMissingCount: 5,
      parasharaLightMissingCount: 5,
      remainingNotReviewedRows: 20,
    },
    workOrderSummary: {
      workOrderRows: 10,
      pendingWorkOrderCount: 10,
      pendingJhoraWorkOrderCount: 5,
      pendingParasharaLightWorkOrderCount: 5,
      blockedCaseCount: 5,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    handoffSummary: {
      caseHandoffRows: 5,
      handoffWorkOrderRows: 10,
      pendingHandoffCount: 10,
      pendingJhoraHandoffCount: 5,
      pendingParasharaLightHandoffCount: 5,
      blockedCaseCount: 5,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    operatorPacketSummary: {
      operatorPacketRows: 5,
      operatorAttachmentSlotRows: 10,
      pendingOperatorPacketCount: 5,
      pendingOperatorAttachmentSlotCount: 10,
      pendingJhoraAttachmentSlotCount: 5,
      pendingParasharaLightAttachmentSlotCount: 5,
      blockedPacketCount: 5,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    operatorPacketQaSummary: {
      operatorPacketQaRows: 5,
      attachmentSlotQaRows: 10,
      blockedPacketQaCount: 5,
      pendingAttachmentSlotQaCount: 10,
      pendingJhoraAttachmentSlotQaCount: 5,
      pendingParasharaLightAttachmentSlotQaCount: 5,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    attachmentReadinessSummary: {
      caseAttachmentReadinessRows: 5,
      attachmentReadinessSlotRows: 10,
      blockedCaseAttachmentCount: 5,
      pendingExternalEvidenceAttachmentCount: 10,
      pendingJhoraExternalAttachmentCount: 5,
      pendingParasharaLightExternalAttachmentCount: 5,
      readyToAttachRows: 0,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    externalIntakeSummary: {
      caseIntakeContractRows: 5,
      attachmentIntakeSlotRows: 10,
      pendingExternalEvidenceIntakeCount: 10,
      pendingJhoraExternalIntakeCount: 5,
      pendingParasharaLightExternalIntakeCount: 5,
      evidenceCollectedCount: 0,
      evidenceUploadedCount: 0,
      evidenceAttachedCount: 0,
      readyToAttachRows: 0,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    externalReceiptSummary: {
      caseReceiptGateRows: 5,
      attachmentReceiptSlotRows: 10,
      pendingExternalEvidenceReceiptCount: 10,
      pendingJhoraReceiptCount: 5,
      pendingParasharaLightReceiptCount: 5,
      evidenceReceivedCount: 0,
      evidenceValidatedCount: 0,
      evidenceUploadedCount: 0,
      evidenceAttachedCount: 0,
      readyToAttachRows: 0,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    externalReceiptManifestSummary: {
      caseReceiptManifestTemplateRows: 5,
      attachmentReceiptManifestTemplateRows: 10,
      pendingExternalEvidenceReceiptManifestCount: 10,
      pendingJhoraReceiptManifestCount: 5,
      pendingParasharaLightReceiptManifestCount: 5,
      receiptManifestReceivedCount: 0,
      evidenceReceivedCount: 0,
      evidenceValidatedCount: 0,
      evidenceFileRecordedCount: 0,
      evidenceHashRecordedCount: 0,
      evidenceUploadedCount: 0,
      evidenceAttachedCount: 0,
      readyToAttachRows: 0,
      readyToMarkRows: 0,
      remainingNotReviewedRows: 20,
    },
    operatorNote: "Evidence must be collected and attached before mark commands are attempted",
    statusCopy: "blocked external evidence receipt manifest template labels",
  };
}

export function buildCoreEvidenceAttachmentGate(): CoreEvidenceAttachmentGate {
  return {
    title: "Core evidence attachment gate",
    schemaVersion: "jyotish-core-evidence-attachment-gate-v1",
    stage: "P59-A",
    attachmentRows: 5,
    operatorAttachmentManifestRows: 5,
    readyToMarkRows: 0,
    blockedRows: 5,
    missingAttachmentSlots: 10,
    attachedEvidenceFiles: 0,
    attachedEvidenceFamilyCount: 0,
    jhoraAttachedCount: 0,
    parasharaLightAttachedCount: 0,
    jhoraMissingCount: 5,
    parasharaLightMissingCount: 5,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    p57EvidenceSlotStatus: {
      jhora_screenshot_or_packet: "missing",
      parashara_light_manual_values_or_packet: "missing",
    },
    attachmentSlotStatus: {
      jhora_screenshot_or_packet: "not_attached",
      parashara_light_manual_values_or_packet: "not_attached",
    },
    readinessStatus: "blocked_missing_evidence",
    attachmentGateStatus: "blocked_no_attached_evidence",
    readyToMarkLabel: "ready_to_mark=false",
    safeNextActions: [
      "collect_jhora_screenshot",
      "attach_parashara_light_manual_values",
      "rerun_evidence_attachment_gate",
      "rerun_preflight_witness_review",
    ],
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
      "mark_jhora_witness_reviewed",
      "mark_parashara_light_witness_reviewed",
    ],
    operatorNote: "Evidence must be attached before mark commands are attempted",
    statusCopy: "external evidence is not attached for every selected intake row",
    cautionCopy: "No mark command should run until evidence is attached",
  };
}

export function buildCoreEvidenceAttachmentWorkOrders(): CoreEvidenceAttachmentWorkOrders {
  return {
    title: "Core evidence attachment work orders",
    schemaVersion: "jyotish-core-evidence-attachment-work-orders-v1",
    stage: "P61-A",
    workOrderRows: 10,
    pendingWorkOrderCount: 10,
    pendingJhoraWorkOrderCount: 5,
    pendingParasharaLightWorkOrderCount: 5,
    blockedCaseCount: 5,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    workOrderStatus: "pending_not_attached",
    caseWorkOrderStatus: "blocked_pending_attachments",
    readyToMarkLabel: "ready_to_mark=false",
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_attachment_work_orders_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "Evidence must be attached before mark commands are attempted; work orders are labels only and do not collect evidence",
    statusCopy: "work orders remain pending because evidence is not attached",
    cautionCopy: "No work order attaches evidence or permits mark commands",
  };
}

export function buildCoreEvidenceAttachmentHandoff(): CoreEvidenceAttachmentHandoff {
  return {
    title: "Core evidence attachment handoff",
    schemaVersion: "jyotish-core-evidence-attachment-handoff-v1",
    stage: "P63-A",
    caseHandoffRows: 5,
    handoffWorkOrderRows: 10,
    pendingHandoffCount: 10,
    pendingJhoraHandoffCount: 5,
    pendingParasharaLightHandoffCount: 5,
    blockedCaseCount: 5,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    handoffStatus: "blocked_pending_operator_evidence",
    caseWorkOrderStatus: "blocked_pending_attachments",
    readyToMarkLabel: "ready_to_mark=false",
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_attachment_handoff_report",
      "build_witness_core_evidence_attachment_work_orders_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "external evidence has not been attached; handoff rows are labels only and do not collect evidence",
    statusCopy: "handoff bundle remains blocked pending operator evidence",
    cautionCopy: "No evidence is attached and no release readiness is claimed",
  };
}

export function buildCoreEvidenceOperatorPackets(): CoreEvidenceOperatorPackets {
  return {
    title: "Core evidence operator packets",
    schemaVersion: "jyotish-core-evidence-operator-packets-v1",
    stage: "P65-A",
    operatorPacketRows: 5,
    operatorAttachmentSlotRows: 10,
    pendingOperatorPacketCount: 5,
    pendingOperatorAttachmentSlotCount: 10,
    pendingJhoraAttachmentSlotCount: 5,
    pendingParasharaLightAttachmentSlotCount: 5,
    blockedPacketCount: 5,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    packetStatus: "blocked_pending_operator_packet_evidence",
    handoffStatus: "blocked_pending_operator_evidence",
    caseWorkOrderStatus: "blocked_pending_attachments",
    evidenceFileStatus: "not_attached",
    readyToMarkLabel: "ready_to_mark=false",
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_operator_packets_report",
      "build_witness_core_evidence_attachment_handoff_report",
      "build_witness_core_evidence_attachment_work_orders_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "external evidence has not been attached; operator packets are labels only and do not collect or attach evidence",
    statusCopy: "operator packet manifest remains blocked pending evidence attachment",
    cautionCopy: "No evidence is attached and no release readiness is claimed",
  };
}

export function buildCoreEvidenceOperatorPacketQa(): CoreEvidenceOperatorPacketQa {
  return {
    title: "Core evidence operator packet QA",
    schemaVersion: "jyotish-core-evidence-operator-packet-qa-v1",
    stage: "P67-A",
    operatorPacketQaRows: 5,
    attachmentSlotQaRows: 10,
    blockedPacketQaCount: 5,
    pendingAttachmentSlotQaCount: 10,
    pendingJhoraAttachmentSlotQaCount: 5,
    pendingParasharaLightAttachmentSlotQaCount: 5,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    qaStatus: "blocked_pending_operator_packet_qa",
    packetStatus: "blocked_pending_operator_packet_evidence",
    attachmentSlotStatus: "not_attached",
    readyToMarkLabel: "ready_to_mark=false",
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_operator_packet_qa_report",
      "build_witness_core_evidence_operator_packets_report",
      "build_witness_core_evidence_attachment_handoff_report",
      "build_witness_core_evidence_attachment_work_orders_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "external evidence has not been attached; operator packets are labels only; mark commands remain blocked",
    statusCopy: "QA preflight remains blocked pending operator packet evidence",
    cautionCopy: "No evidence is attached and no release readiness is claimed",
  };
}

export function buildCoreEvidenceOperatorPacketAttachmentReadiness(): CoreEvidenceOperatorPacketAttachmentReadiness {
  return {
    title: "Core evidence operator packet attachment readiness",
    schemaVersion: "jyotish-core-evidence-operator-packet-attachment-readiness-v1",
    stage: "P69-A",
    caseAttachmentReadinessRows: 5,
    attachmentReadinessSlotRows: 10,
    blockedCaseAttachmentCount: 5,
    pendingExternalEvidenceAttachmentCount: 10,
    pendingJhoraExternalAttachmentCount: 5,
    pendingParasharaLightExternalAttachmentCount: 5,
    readyToAttachRows: 0,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    slotFamilies: [
      "jhora_screenshot_or_packet",
      "parashara_light_manual_values_or_packet",
    ],
    readinessStatus: "blocked_pending_external_evidence_attachment",
    qaStatus: "blocked_pending_operator_packet_qa",
    packetStatus: "blocked_pending_operator_packet_evidence",
    attachmentSlotStatus: "not_attached",
    readyToAttachLabel: "ready_to_attach=false",
    readyToMarkLabel: "ready_to_mark=false",
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_operator_packet_attachment_readiness_report",
      "build_witness_core_evidence_operator_packet_qa_report",
      "build_witness_core_evidence_operator_packets_report",
      "build_witness_core_evidence_attachment_handoff_report",
      "build_witness_core_evidence_attachment_work_orders_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "external evidence has not been attached; readiness rows are labels only; collection/upload/mark commands are not executed",
    statusCopy: "attachment-readiness labels exist while external evidence remains not attached",
    cautionCopy: "ready-to-attach is false; ready-to-mark is false; release remains blocked",
  };
}

export function buildCoreEvidenceExternalIntakeContract(): CoreEvidenceExternalIntakeContract {
  return {
    title: "Core evidence external intake contract",
    schemaVersion: "jyotish-core-evidence-external-intake-contract-v1",
    stage: "P71-A",
    caseIntakeContractRows: 5,
    attachmentIntakeSlotRows: 10,
    pendingExternalEvidenceIntakeCount: 10,
    pendingJhoraExternalIntakeCount: 5,
    pendingParasharaLightExternalIntakeCount: 5,
    evidenceCollectedCount: 0,
    evidenceUploadedCount: 0,
    evidenceAttachedCount: 0,
    readyToAttachRows: 0,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    slotFamilies: [
      "jhora_screenshot_or_packet",
      "parashara_light_manual_values_or_packet",
    ],
    intakeStatus: "blocked_pending_external_evidence_intake",
    readinessStatus: "blocked_pending_external_evidence_attachment",
    qaStatus: "blocked_pending_operator_packet_qa",
    packetStatus: "blocked_pending_operator_packet_evidence",
    evidenceFileStatus: "not_attached",
    evidenceCollectionStatus: "not_started",
    evidenceUploadStatus: "not_started",
    evidenceAttachmentStatus: "not_attached",
    readyToAttachLabel: "ready_to_attach=false",
    readyToMarkLabel: "ready_to_mark=false",
    evidenceCollectedLabel: "evidence_collected=false",
    evidenceUploadedLabel: "evidence_uploaded=false",
    evidenceAttachedLabel: "evidence_attached=false",
    safeIntakeLabels: [
      "request_jhora_screenshot_or_packet",
      "request_parashara_light_manual_values_or_packet",
      "receive_external_evidence_from_human",
      "rerun_external_intake_contract_report",
      "rerun_operator_packet_attachment_readiness_report",
      "rerun_operator_packet_qa_report",
      "rerun_attachment_gate_report",
      "preflight_witness_review",
    ],
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_external_intake_contract_report",
      "build_witness_core_evidence_operator_packet_attachment_readiness_report",
      "build_witness_core_evidence_operator_packet_qa_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "external evidence has not been collected, uploaded, or attached; intake rows are labels only; mark commands are not executed",
    statusCopy: "human-provided external evidence intake is requested as labels only",
    cautionCopy: "nothing is collected, uploaded, or attached; ready-to-attach is false; ready-to-mark is false; release remains blocked",
  };
}

export function buildCoreEvidenceExternalReceiptGate(): CoreEvidenceExternalReceiptGate {
  return {
    title: "Core evidence external receipt gate",
    schemaVersion: "jyotish-core-evidence-external-receipt-gate-v1",
    stage: "P73-A",
    caseReceiptGateRows: 5,
    attachmentReceiptSlotRows: 10,
    pendingExternalEvidenceReceiptCount: 10,
    pendingJhoraReceiptCount: 5,
    pendingParasharaLightReceiptCount: 5,
    evidenceReceivedCount: 0,
    evidenceValidatedCount: 0,
    evidenceUploadedCount: 0,
    evidenceAttachedCount: 0,
    readyToAttachRows: 0,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    paritySuccessClaimed: false,
    releaseReadyClaimed: false,
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    slotFamilies: [
      "jhora_screenshot_or_packet",
      "parashara_light_manual_values_or_packet",
    ],
    receiptGateStatus: "blocked_pending_external_evidence_receipts",
    intakeStatus: "blocked_pending_external_evidence_intake",
    readinessStatus: "blocked_pending_external_evidence_attachment",
    evidenceReceiptStatus: "not_received",
    evidenceValidationStatus: "not_started",
    evidenceFileStatus: "not_attached",
    evidenceUploadStatus: "not_started",
    evidenceAttachmentStatus: "not_attached",
    readyToAttachLabel: "ready_to_attach=false",
    readyToMarkLabel: "ready_to_mark=false",
    evidenceReceivedLabel: "evidence_received_count=0",
    evidenceValidatedLabel: "evidence_validated_count=0",
    evidenceUploadedLabel: "evidence_uploaded_count=0",
    evidenceAttachedLabel: "evidence_attached_count=0",
    paritySuccessClaimedLabel: "parity_success_claimed=false",
    releaseReadyClaimedLabel: "release_ready_claimed=false",
    safeReceiptLabels: [
      "await_jhora_screenshot_or_packet_receipt",
      "await_parashara_light_manual_values_or_packet_receipt",
      "record_external_evidence_receipt_manifest",
      "rerun_external_receipt_gate_report",
      "rerun_external_intake_contract_report",
      "rerun_operator_packet_attachment_readiness_report",
      "rerun_attachment_gate_report",
      "preflight_witness_review",
    ],
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_external_receipt_gate_report",
      "build_witness_core_evidence_external_intake_contract_report",
      "build_witness_core_evidence_operator_packet_attachment_readiness_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "external evidence receipts have not been received or validated; receipt rows are labels only; collection/upload/attachment/mark commands are not executed",
    statusCopy: "external evidence receipt gate remains blocked",
    cautionCopy: "nothing is received, validated, uploaded, or attached; ready-to-attach is false; ready-to-mark is false; release remains blocked",
  };
}

export function buildCoreEvidenceExternalReceiptManifestTemplates(): CoreEvidenceExternalReceiptManifestTemplates {
  return {
    title: "Core evidence external receipt manifest templates",
    schemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1",
    stage: "P75-A",
    caseReceiptManifestTemplateRows: 5,
    attachmentReceiptManifestTemplateRows: 10,
    pendingExternalEvidenceReceiptManifestCount: 10,
    pendingJhoraReceiptManifestCount: 5,
    pendingParasharaLightReceiptManifestCount: 5,
    receiptManifestReceivedCount: 0,
    evidenceReceivedCount: 0,
    evidenceValidatedCount: 0,
    evidenceFileRecordedCount: 0,
    evidenceHashRecordedCount: 0,
    evidenceUploadedCount: 0,
    evidenceAttachedCount: 0,
    readyToAttachRows: 0,
    readyToMarkRows: 0,
    remainingNotReviewedRows: 20,
    releaseGateStatus: "blocked",
    commandSmokeMatrixStatus: "ready",
    paritySuccessClaimed: false,
    releaseReadyClaimed: false,
    selectedCaseIds: [
      "vrindavan-1990-08-15-1024",
      "delhi-india-1947-08-15-000001",
      "mayapur-2001-02-03-0910",
      "new-york-2026-03-08-0155",
      "new-york-2026-11-01-0130",
    ],
    slotFamilies: [
      "jhora_screenshot_or_packet",
      "parashara_light_manual_values_or_packet",
    ],
    receiptManifestTemplateStatus: "blocked_pending_external_evidence_receipt_manifests",
    receiptGateStatus: "blocked_pending_external_evidence_receipts",
    intakeStatus: "blocked_pending_external_evidence_intake",
    readinessStatus: "blocked_pending_external_evidence_attachment",
    receiptManifestStatus: "not_received",
    evidenceValidationStatus: "not_started",
    evidenceFileStatus: "not_attached",
    evidenceHashStatus: "not_recorded",
    evidenceUploadStatus: "not_started",
    evidenceAttachmentStatus: "not_attached",
    readyToAttachLabel: "ready_to_attach=false",
    readyToMarkLabel: "ready_to_mark=false",
    receiptManifestReceivedLabel: "receipt_manifest_received_count=0",
    evidenceReceivedLabel: "evidence_received_count=0",
    evidenceValidatedLabel: "evidence_validated_count=0",
    evidenceFileRecordedLabel: "evidence_file_recorded_count=0",
    evidenceHashRecordedLabel: "evidence_hash_recorded_count=0",
    evidenceUploadedLabel: "evidence_uploaded_count=0",
    evidenceAttachedLabel: "evidence_attached_count=0",
    paritySuccessClaimedLabel: "parity_success_claimed=false",
    releaseReadyClaimedLabel: "release_ready_claimed=false",
    safeManifestTemplateLabels: [
      "await_jhora_receipt_manifest",
      "await_parashara_light_receipt_manifest",
      "record_external_evidence_receipt_manifest",
      "rerun_external_receipt_manifest_templates_report",
      "rerun_external_receipt_gate_report",
      "rerun_external_intake_contract_report",
      "rerun_operator_packet_attachment_readiness_report",
      "rerun_attachment_gate_report",
      "preflight_witness_review",
    ],
    safeRequiredManifestFields: [
      "case_id",
      "evidence_family",
      "external_tool_label",
      "human_receipt_timestamp_utc",
      "redacted_receipt_manifest_id",
      "operator_receipt_note_label",
      "no_raw_values_in_manifest",
      "no_private_paths_in_manifest",
      "no_secrets_in_manifest",
    ],
    safeValidationCommandFamilies: [
      "build_witness_core_evidence_external_receipt_manifest_templates_report",
      "build_witness_core_evidence_external_receipt_gate_report",
      "build_witness_core_evidence_external_intake_contract_report",
      "build_witness_core_evidence_operator_packet_attachment_readiness_report",
      "build_witness_core_evidence_attachment_gate_report",
      "preflight_witness_review",
    ],
    operatorNote: "receipt manifests have not arrived; template rows are labels only; no evidence file, hash, upload, attachment, or mark command is executed",
    statusCopy: "external evidence receipt manifest templates remain blocked",
    cautionCopy: "no manifest, evidence, file, hash, upload, attachment, or mark command has happened; ready-to-attach is false; ready-to-mark is false; release remains blocked",
  };
}

function skippedCount(payload: ParityPayload): number {
  let total = 0;
  for (const [key, value] of Object.entries(payload)) {
    if (!key.endsWith("_summary") || key === "summary" || !isRecord(value)) {
      continue;
    }
    for (const row of Object.values(value)) {
      if (isRecord(row)) {
        total += safeNumber(row.skipped);
      }
    }
  }
  return total;
}

function readinessGapCount(payload: ParityPayload): number {
  const readiness = payload.readiness_summary;
  if (!isRecord(readiness)) {
    return 0;
  }
  return Object.values(readiness).reduce<number>((total, row) => {
    if (!isRecord(row)) {
      return total;
    }
    return total + safeNumber(row.actual_missing);
  }, 0);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function safeNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}
