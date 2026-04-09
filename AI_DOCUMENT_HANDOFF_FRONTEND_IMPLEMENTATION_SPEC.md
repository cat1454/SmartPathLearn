# AI Document Handoff Frontend Implementation Spec

## Muc tieu

Tai lieu nay noi tiep:

- `AI_DOCUMENT_HANDOFF_WORKFLOW_V2.md`
- `AI_DOCUMENT_HANDOFF_WEB_SCREEN_SPEC.md`

Muc tieu la doi spec tu muc screen/flow sang muc frontend co the code ngay:

- route ro rang
- component tree ro rang
- props/data contract ro rang
- state va validation boundary ro rang

Tai lieu nay chi spec frontend. No khong thay the contract nghiep vu o V2.

## Nguyen tac implement

1. Web chi dieu phoi prompt, nhan payload, validate, preview, luu.
2. Web khong tu sinh noi dung va khong tu cham runtime.
3. Moi route chi co 1 trach nhiem chinh.
4. Parse va validation phai deterministic.
5. Neu payload sai format, UI chi duoc reject + dua repair prompt.
6. Moi `activity_type` phai di qua cung mot `activity envelope`, chi `activity_data` va `feedback` thay doi theo format.

## Route Map

### Route 1: `/handoff/source-packs/new`

Muc dich:

- copy prompt tao `source_pack`
- paste payload vao web
- validate
- save thanh `source_pack_ref`

### Route 2: `/handoff/source-packs/:sourcePackId`

Muc dich:

- xem `source_pack` da luu
- xem lesson context
- di tiep sang buoc tao activity

### Route 3: `/handoff/activities/new?sourcePackId=:id`

Muc dich:

- chon 1 `activity_type`
- copy prompt authoring
- paste `activity_authoring` payload
- validate va save activity

### Route 4: `/handoff/activities/:activityId`

Muc dich:

- xem activity da duoc import
- preview format theo `activity_type`
- copy huong dan de giao cho hoc sinh
- di tiep sang submission hoac feedback

### Route 5: `/handoff/activities/:activityId/submission`

Muc dich:

- nhap bai lam hoc sinh
- chuan hoa `student_submission`
- copy prompt feedback

### Route 6: `/handoff/activities/:activityId/feedback`

Muc dich:

- paste `activity_feedback` payload
- validate
- luu feedback
- render ket qua de hoc sinh/doc giao vien xem lai

## Goi y file structure

```text
src/
  features/
    handoff/
      routes/
        SourcePackCreatePage.tsx
        SourcePackDetailPage.tsx
        ActivityCreatePage.tsx
        ActivityDetailPage.tsx
        ActivitySubmissionPage.tsx
        ActivityFeedbackPage.tsx
      components/
        HandoffLayout.tsx
        StepRail.tsx
        ContextPanel.tsx
        PromptCard.tsx
        PayloadPasteBox.tsx
        ValidationPanel.tsx
        RepairPromptCard.tsx
        SummaryCard.tsx
        ActivityTypePicker.tsx
        ActivityPreview.tsx
        SubmissionBox.tsx
        FeedbackSummary.tsx
      contracts/
        handoff.types.ts
        handoff.schemas.ts
        handoff.issue-codes.ts
      lib/
        markers.ts
        parseMarkedJson.ts
        validation.ts
        prompt-builders.ts
        mappers.ts
      services/
        sourcePack.service.ts
        activity.service.ts
        feedback.service.ts
```

## Shared Types

```ts
export type WorkflowStep =
  | 'select_lesson'
  | 'source_pack'
  | 'choose_format'
  | 'authoring_payload'
  | 'student_submission'
  | 'feedback_payload';

export type ActivityType =
  | 'case_mission'
  | 'error_hunt'
  | 'explain_back'
  | 'mini_project'
  | 'debate_defend';

export type PayloadType =
  | 'source_pack'
  | 'activity_authoring'
  | 'activity_feedback';

export type PayloadMarker =
  | 'SOURCE_PACK_V1'
  | 'ACTIVITY_PAYLOAD_V2'
  | 'ACTIVITY_FEEDBACK_V2';

export type LoadStatus =
  | 'idle'
  | 'loading'
  | 'validating'
  | 'valid'
  | 'invalid'
  | 'saving'
  | 'saved'
  | 'load_error';

export type ResponseType =
  | 'free_text'
  | 'bullet_points'
  | 'short_essay';

export interface ValidationIssue {
  code:
    | 'missing_marker'
    | 'invalid_marker_pair'
    | 'text_outside_marker'
    | 'json_parse_failed'
    | 'payload_type_invalid'
    | 'activity_type_invalid'
    | 'response_type_invalid'
    | 'missing_required_field'
    | 'invalid_field_type'
    | 'unknown_field'
    | 'empty_array'
    | 'empty_string'
    | 'reference_not_found'
    | 'route_mismatch';
  severity: 'error' | 'warning';
  path: string;
  message: string;
  expected?: string;
}

export interface ValidationResult<T> {
  ok: boolean;
  marker: PayloadMarker | null;
  normalized: T | null;
  issues: ValidationIssue[];
  rawJson: unknown | null;
}
```

## Payload Contracts

### Source Pack

```ts
export interface SourcePackPayload {
  payload_type: 'source_pack';
  source_pack_ref: string | null;
  subject: string;
  grade_level: string;
  chapter_title: string;
  lesson_title: string;
  learning_objectives: string[];
  key_concepts: string[];
  formulas: string[];
  events_or_milestones: string[];
  examples: string[];
  common_mistakes: string[];
  prerequisites: string[];
  source_notes: string[];
  coverage_warning: string;
}

export interface StoredSourcePack {
  id: string;
  created_at: string;
  updated_at: string;
  payload: SourcePackPayload;
}
```

### Activity Authoring Envelope

```ts
export interface ActivityEnvelopeBase {
  payload_type: 'activity_authoring';
  activity_type: ActivityType;
  activity_id: string | null;
  source_pack_ref: string;
  document_title: string;
  lesson_title: string;
  student_level: string;
  instructions: string[];
}

export interface CaseMissionData {
  scenario: string;
  task: string;
  expected_points: string[];
  success_criteria: string[];
  hint_optional?: string | null;
}

export interface ErrorHuntData {
  artifact: string;
  error_count_expected: number;
  error_categories: string[];
  reference_points: string[];
}

export interface ExplainBackData {
  teaching_prompt: string;
  target_audience: string;
  expected_points: string[];
  clarity_rubric: string[];
}

export interface MiniProjectData {
  brief: string;
  deliverable_type: string;
  constraints: string[];
  rubric: string[];
}

export interface DebateDefendData {
  claim: string;
  position_task: string;
  evidence_rules: string[];
  rubric: string[];
}

export type ActivityData =
  | CaseMissionData
  | ErrorHuntData
  | ExplainBackData
  | MiniProjectData
  | DebateDefendData;

export interface ActivityAuthoringPayload extends ActivityEnvelopeBase {
  activity_data: ActivityData;
}

export interface StoredActivity {
  id: string;
  created_at: string;
  updated_at: string;
  source_pack_id: string;
  payload: ActivityAuthoringPayload;
}
```

### Student Submission

```ts
export interface StudentSubmission {
  response_type: ResponseType;
  response_content: string;
}
```

### Activity Feedback Envelope

```ts
export interface FeedbackBase {
  overall_verdict: string;
  strengths: string[];
  gaps: string[];
  misconceptions: string[];
  next_step: string;
  score_optional?: string | number | null;
}

export interface CaseMissionFeedbackExtra {
  missed_expected_points: string[];
}

export interface ErrorHuntFeedbackExtra {
  missed_errors: string[];
  false_positives: string[];
}

export interface ExplainBackFeedbackExtra {
  missing_points: string[];
  clarity_notes: string[];
}

export interface MiniProjectFeedbackExtra {
  rubric_breakdown: Array<{
    criterion: string;
    verdict: string;
    note: string;
  }>;
}

export interface DebateDefendFeedbackExtra {
  argument_quality: string;
  evidence_quality: string;
  logic_gaps: string[];
}

export type ActivityFeedbackData =
  | (FeedbackBase & Partial<CaseMissionFeedbackExtra>)
  | (FeedbackBase & Partial<ErrorHuntFeedbackExtra>)
  | (FeedbackBase & Partial<ExplainBackFeedbackExtra>)
  | (FeedbackBase & Partial<MiniProjectFeedbackExtra>)
  | (FeedbackBase & Partial<DebateDefendFeedbackExtra>);

export interface ActivityFeedbackPayload {
  payload_type: 'activity_feedback';
  activity_type: ActivityType;
  activity_id: string;
  student_submission: StudentSubmission;
  feedback: ActivityFeedbackData;
}

export interface StoredFeedback {
  id: string;
  created_at: string;
  updated_at: string;
  activity_id: string;
  payload: ActivityFeedbackPayload;
}
```

## Shared Utility Contracts

```ts
export interface ParseMarkedJsonParams {
  rawText: string;
  marker: PayloadMarker;
}

export interface BuildPromptParams {
  sourcePack?: SourcePackPayload;
  activityType?: ActivityType;
  activity?: ActivityAuthoringPayload;
  submission?: StudentSubmission;
}

export interface RepairPromptParams {
  marker: PayloadMarker;
  rawText: string;
  issues: ValidationIssue[];
}
```

Frontend utility functions:

```ts
export function parseMarkedJson(params: ParseMarkedJsonParams): ValidationResult<unknown>;
export function validateSourcePack(rawText: string): ValidationResult<SourcePackPayload>;
export function validateActivityAuthoring(rawText: string): ValidationResult<ActivityAuthoringPayload>;
export function validateActivityFeedback(rawText: string): ValidationResult<ActivityFeedbackPayload>;
export function buildSourcePackPrompt(params: BuildPromptParams): string;
export function buildAuthoringPrompt(params: BuildPromptParams): string;
export function buildFeedbackPrompt(params: BuildPromptParams): string;
export function buildRepairPrompt(params: RepairPromptParams): string;
```

Rule:

- `parseMarkedJson` chi lo marker + parse JSON
- `validate*` lo schema + field requirement + activity-specific required field
- `build*Prompt` khong duoc noi them logic nghiep vu ngoai spec
- normalized output co the doi `source_pack_ref` / `activity_id` rong thanh `null` truoc luc save

## Shared Component Contracts

### `HandoffLayout`

```ts
interface HandoffLayoutProps {
  currentStep: WorkflowStep;
  completedSteps: WorkflowStep[];
  headerTitle: string;
  headerDescription?: string;
  contextPanel: React.ReactNode;
  children: React.ReactNode;
  primaryAction?: React.ReactNode;
}
```

Trach nhiem:

- render shell 3 cot / responsive
- host `StepRail`
- host page title
- host sticky CTA area

### `StepRail`

```ts
interface StepRailProps {
  currentStep: WorkflowStep;
  completedSteps: WorkflowStep[];
  allowNavigation?: boolean;
  routeMap: Record<WorkflowStep, string>;
}
```

### `ContextPanel`

```ts
interface ContextPanelProps {
  sourcePack?: SourcePackPayload | null;
  activity?: ActivityAuthoringPayload | null;
  feedback?: ActivityFeedbackPayload | null;
  markerHint?: PayloadMarker | null;
  quickNotes?: string[];
}
```

### `PromptCard`

```ts
interface PromptCardProps {
  title: string;
  promptText: string;
  copyLabel?: string;
  helperText?: string;
}
```

### `PayloadPasteBox`

```ts
interface PayloadPasteBoxProps {
  value: string;
  onChange: (next: string) => void;
  expectedMarker: PayloadMarker;
  status: LoadStatus;
  placeholder?: string;
  minRows?: number;
}
```

### `ValidationPanel`

```ts
interface ValidationPanelProps {
  result: ValidationResult<unknown> | null;
  emptyMessage?: string;
}
```

### `RepairPromptCard`

```ts
interface RepairPromptCardProps {
  visible: boolean;
  promptText: string;
}
```

### `SummaryCard`

```ts
interface SummaryCardProps {
  title: string;
  rows: Array<{
    label: string;
    value: string | number | null | undefined;
  }>;
}
```

### `ActivityTypePicker`

```ts
interface ActivityTypeOption {
  value: ActivityType;
  title: string;
  description: string;
  status: 'active' | 'coming_soon';
}

interface ActivityTypePickerProps {
  options: ActivityTypeOption[];
  value: ActivityType | null;
  onChange: (next: ActivityType) => void;
}
```

### `ActivityPreview`

```ts
interface ActivityPreviewProps {
  activity: ActivityAuthoringPayload;
}
```

Rule render:

- `case_mission`: scenario -> task -> expected points -> success criteria
- `error_hunt`: artifact -> error count -> categories -> reference points
- `explain_back`: teaching prompt -> audience -> expected points -> clarity rubric
- `mini_project`: brief -> deliverable -> constraints -> rubric
- `debate_defend`: claim -> position task -> evidence rules -> rubric

### `SubmissionBox`

```ts
interface SubmissionBoxProps {
  value: StudentSubmission;
  onChange: (next: StudentSubmission) => void;
}
```

### `FeedbackSummary`

```ts
interface FeedbackSummaryProps {
  activityType: ActivityType;
  feedback: ActivityFeedbackPayload;
}
```

## Route-by-Route Implementation Spec

### Route 1: `SourcePackCreatePage`

#### Loader data

```ts
interface SourcePackCreateLoaderData {
  documentTitle?: string;
  lessonTitle?: string;
  studentLevel?: string;
}
```

#### Local page state

```ts
interface SourcePackCreatePageState {
  rawPayloadText: string;
  validation: ValidationResult<SourcePackPayload> | null;
  status: LoadStatus;
}
```

#### Component tree

```text
SourcePackCreatePage
  HandoffLayout
    StepRail
    PageHeader
    Workspace
      PromptCard
      PayloadPasteBox
      ValidationPanel
      RepairPromptCard
      PrimaryActionBar
    ContextPanel
      SummaryCard
      SummaryCard
```

#### Child contract notes

- `PromptCard.promptText` = source pack prompt built from lesson context if available
- `PayloadPasteBox.expectedMarker` = `SOURCE_PACK_V1`
- `ValidationPanel.result` = output of `validateSourcePack`
- `Primary action` = `Validate and save`
- `source_pack_ref` duoc phep rong trong payload tao moi; backend se sinh luc save

#### Save contract

Input:

```ts
interface SaveSourcePackInput {
  payload: SourcePackPayload;
}
```

Output:

```ts
interface SaveSourcePackResult {
  id: string;
  payload: SourcePackPayload;
}
```

Route transition:

- save success -> `/handoff/source-packs/:sourcePackId`

### Route 2: `SourcePackDetailPage`

#### Loader data

```ts
interface SourcePackDetailLoaderData {
  sourcePack: StoredSourcePack;
}
```

#### Component tree

```text
SourcePackDetailPage
  HandoffLayout
    StepRail
    PageHeader
    Workspace
      SummaryCard
      SummaryCard
      SummaryCard
      SecondaryActionRow
    ContextPanel
      SummaryCard
      PromptCard
```

#### Render requirements

- hien du `subject`, `grade_level`, `chapter_title`, `lesson_title`
- hien list sections:
  - `learning_objectives`
  - `key_concepts`
  - `common_mistakes`
  - `coverage_warning`
- CTA chinh = `Tao activity`

#### Route transition

- CTA -> `/handoff/activities/new?sourcePackId=:id`

### Route 3: `ActivityCreatePage`

#### Loader data

```ts
interface ActivityCreateLoaderData {
  sourcePack: StoredSourcePack;
  activityOptions: ActivityTypeOption[];
}
```

#### Local page state

```ts
interface ActivityCreatePageState {
  selectedType: ActivityType | null;
  rawPayloadText: string;
  validation: ValidationResult<ActivityAuthoringPayload> | null;
  status: LoadStatus;
}
```

#### Component tree

```text
ActivityCreatePage
  HandoffLayout
    StepRail
    PageHeader
    Workspace
      SummaryCard
      ActivityTypePicker
      PromptCard
      PayloadPasteBox
      ValidationPanel
      RepairPromptCard
      PrimaryActionBar
    ContextPanel
      SummaryCard
      SummaryCard
```

#### Contract rules

- `ActivityTypePicker.value` la state goc de build prompt
- `PayloadPasteBox.expectedMarker` = `ACTIVITY_PAYLOAD_V2`
- `validateActivityAuthoring` phai check:
  - `payload_type === activity_authoring`
  - `source_pack_ref` trung voi loader source pack
  - `activity_type` trung voi `selectedType`
  - `activity_id` ton tai; neu rong thi backend sinh luc save
  - `activity_data` dung schema theo format

#### Save contract

Input:

```ts
interface SaveActivityInput {
  sourcePackId: string;
  payload: ActivityAuthoringPayload;
}
```

Output:

```ts
interface SaveActivityResult {
  id: string;
  payload: ActivityAuthoringPayload;
}
```

#### Route transition

- save success -> `/handoff/activities/:activityId`

### Route 4: `ActivityDetailPage`

#### Loader data

```ts
interface ActivityDetailLoaderData {
  sourcePack: StoredSourcePack;
  activity: StoredActivity;
  latestFeedback?: StoredFeedback | null;
}
```

#### Component tree

```text
ActivityDetailPage
  HandoffLayout
    StepRail
    PageHeader
    Workspace
      SummaryCard
      ActivityPreview
      PromptCard
      SecondaryActionRow
    ContextPanel
      SummaryCard
      SummaryCard
      SummaryCard
```

#### Render requirements

- `ActivityPreview` phai branch thuong minh theo `activity.payload.activity_type`
- `PromptCard` hien prompt giao bai cho hoc sinh neu can copy ra ngoai
- CTA chinh = `Nhap bai lam`
- CTA phu = `Nhap feedback`

#### Route transition

- CTA chinh -> `/handoff/activities/:activityId/submission`
- CTA phu -> `/handoff/activities/:activityId/feedback`

### Route 5: `ActivitySubmissionPage`

#### Loader data

```ts
interface ActivitySubmissionLoaderData {
  sourcePack: StoredSourcePack;
  activity: StoredActivity;
}
```

#### Local page state

```ts
interface ActivitySubmissionPageState {
  submission: StudentSubmission;
  status: LoadStatus;
}
```

#### Component tree

```text
ActivitySubmissionPage
  HandoffLayout
    StepRail
    PageHeader
    Workspace
      ActivityPreview
      SubmissionBox
      PromptCard
      PrimaryActionBar
    ContextPanel
      SummaryCard
      SummaryCard
```

#### Save contract

Input:

```ts
interface SaveSubmissionInput {
  activityId: string;
  submission: StudentSubmission;
}
```

Output:

```ts
interface SaveSubmissionResult {
  activityId: string;
  submission: StudentSubmission;
}
```

#### Prompt contract

`PromptCard.promptText` phai build tu:

- `activity.payload`
- `student_submission`
- feedback prompt dung voi `activity_type`

#### Route transition

- save success co the:
  - o lai de copy prompt
  - hoac di tiep -> `/handoff/activities/:activityId/feedback`

### Route 6: `ActivityFeedbackPage`

#### Loader data

```ts
interface ActivityFeedbackLoaderData {
  sourcePack: StoredSourcePack;
  activity: StoredActivity;
  submission?: StudentSubmission | null;
  latestFeedback?: StoredFeedback | null;
}
```

#### Local page state

```ts
interface ActivityFeedbackPageState {
  rawPayloadText: string;
  validation: ValidationResult<ActivityFeedbackPayload> | null;
  status: LoadStatus;
}
```

#### Component tree

```text
ActivityFeedbackPage
  HandoffLayout
    StepRail
    PageHeader
    Workspace
      SummaryCard
      SubmissionPreview
      PayloadPasteBox
      ValidationPanel
      RepairPromptCard
      FeedbackSummary
      PrimaryActionBar
    ContextPanel
      SummaryCard
      SummaryCard
      PromptCard
```

#### Contract rules

- `PayloadPasteBox.expectedMarker` = `ACTIVITY_FEEDBACK_V2`
- `validateActivityFeedback` phai check:
  - `payload_type === activity_feedback`
  - `activity_id` trung route param
  - `activity_type` trung activity da luu
  - `student_submission` co `response_type`, `response_content`
  - `feedback` co it nhat:
    - `strengths`
    - `gaps`
    - `next_step`

#### Save contract

Input:

```ts
interface SaveFeedbackInput {
  activityId: string;
  payload: ActivityFeedbackPayload;
}
```

Output:

```ts
interface SaveFeedbackResult {
  id: string;
  payload: ActivityFeedbackPayload;
}
```

#### Route behavior

- khi feedback valid va chua save: render `FeedbackSummary` bang du lieu normalized tam thoi
- khi save xong: page reload loader hoac optimistic update

## Validation Matrix

### `SOURCE_PACK_V1`

Bat buoc:

- marker dung cap
- `payload_type = source_pack`
- `source_pack_ref` phai ton tai, co the rong trong payload tao moi
- cac field root phai ton tai
- field string duoc rong
- field array duoc rong nhung phai dung type

Root field bat buoc:

- `formulas`
- `events_or_milestones`
- `source_notes`

Warning hop le:

- `examples` rong
- `prerequisites` rong
- `coverage_warning` ngan

### `ACTIVITY_PAYLOAD_V2`

Bat buoc chung:

- marker dung cap
- `payload_type = activity_authoring`
- `activity_type` nam trong 5 gia tri Wave 1
- `activity_id` phai ton tai; co the rong trong create flow
- `source_pack_ref` ton tai
- `instructions` phai ton tai va la array string; empty thi warning

Bat buoc theo format:

- `case_mission`: `scenario`, `task`, `expected_points`, `success_criteria`
- `error_hunt`: `artifact`, `error_count_expected`, `error_categories`, `reference_points`
- `explain_back`: `teaching_prompt`, `target_audience`, `expected_points`, `clarity_rubric`
- `mini_project`: `brief`, `deliverable_type`, `constraints`, `rubric`
- `debate_defend`: `claim`, `position_task`, `evidence_rules`, `rubric`

### `ACTIVITY_FEEDBACK_V2`

Bat buoc chung:

- marker dung cap
- `payload_type = activity_feedback`
- `activity_id` ton tai
- `student_submission.response_type` chi nhan:
  - `free_text`
  - `bullet_points`
  - `short_essay`
- `student_submission.response_type` ton tai
- `student_submission.response_content` khong rong
- `feedback.overall_verdict` khong rong
- `feedback.strengths` la array
- `feedback.gaps` la array
- `feedback.next_step` khong rong
- `feedback.score_optional` neu co la string, number, hoac null

Bat buoc theo format:

- `case_mission`: neu co thi validate `missed_expected_points` la array
- `error_hunt`: neu co thi validate `missed_errors`, `false_positives` la array
- `explain_back`: neu co thi validate `missing_points`, `clarity_notes` la array
- `mini_project`: neu co thi validate `rubric_breakdown` la array object
- `debate_defend`: neu co thi validate `argument_quality`, `evidence_quality` la string

## Suggested Hooks

```ts
export function useSourcePackCreateFlow(): {
  state: SourcePackCreatePageState;
  setRawPayloadText(next: string): void;
  validate(): void;
  save(): Promise<void>;
};

export function useActivityAuthoringFlow(sourcePack: StoredSourcePack): {
  state: ActivityCreatePageState;
  setSelectedType(next: ActivityType): void;
  setRawPayloadText(next: string): void;
  validate(): void;
  save(): Promise<void>;
};

export function useSubmissionFlow(activity: StoredActivity): {
  state: ActivitySubmissionPageState;
  setSubmission(next: StudentSubmission): void;
  save(): Promise<void>;
  buildPrompt(): string;
};

export function useFeedbackFlow(activity: StoredActivity): {
  state: ActivityFeedbackPageState;
  setRawPayloadText(next: string): void;
  validate(): void;
  save(): Promise<void>;
};
```

Rule:

- hook khong render HTML
- hook chi giu state, validation, service call, route transition side effect

## Page-level Loading and Error States

Tat ca route detail phai co 3 state nen:

1. `loading`
2. `load_error`
3. `ready`

Tat ca route paste payload phai co 4 state thao tac:

1. `idle`
2. `validating`
3. `invalid`
4. `saving` / `saved`

Khong route nao duoc tron `load_error` voi `validation error`.

## Acceptance Checklist Cho Dev

1. Moi route render duoc voi mock data doc lap.
2. `ActivityPreview` khong can if/else ro roi trong page; branch logic dong goi trong component rieng.
3. `validateSourcePack`, `validateActivityAuthoring`, `validateActivityFeedback` tra ve issue code on dinh de UI map message.
4. UI luon cho copy lai prompt va repair prompt.
5. UI khong nhan payload prose tu do neu thieu marker.
6. `activity_type` la source of truth cho ca renderer, validator, va feedback parser.
7. Save action chi mo khi payload da `valid`.
8. Link nguoc giua 3 tai lieu phai ton tai:
   - workflow V2
   - screen spec
   - implementation spec nay

## Scope chua lam trong vong nay

- runtime branching cho `decision_path`
- timer/stateful play cho `speed_challenge`
- analytics / teacher dashboard
- API schema DB implementation chi tiet
- them WYSIWYG editor; Wave 1 uu tien plain textarea + strict JSON paste
