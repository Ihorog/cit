// MOCK — no real OCR
export type HomeworkItem = {
  subject: string;
  task: string;
  page?: number;
  number?: number;
  type: 'read' | 'write' | 'solve' | 'other';
  due?: string;
};

export function parseHomework(text: string): HomeworkItem {
  return {
    subject: 'Math',
    task: text,
    page: 42,
    number: 3,
    type: 'solve',
    due: new Date(Date.now() + 86400000).toISOString(),
  };
}
