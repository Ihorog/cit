export type FamilyMember = {
  id: string;
  realName: string;
  alias: string;
  birthDate: string;
  role: 'papa' | 'mama' | 'child' | 'other';
};

export type FamilyGroup = {
  id: string;
  name: string;
  members: FamilyMember[];
};

export type FocusObject = {
  id: string;
  title: string;
  description?: string;
  importance: number;
  urgency: number;
  timeRelevance: number;
  ciAlignment: number;
  clarity: number;
  dueDate?: string;
  assignedTo?: string;
};

export type AppState = {
  activeGroup: FamilyGroup;
  mainFocus: FocusObject | null;
  chatOpen: boolean;
  voiceActive: boolean;
};
