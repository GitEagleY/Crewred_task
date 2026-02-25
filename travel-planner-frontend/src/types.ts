export interface Place {
  id: number;
  external_api_id: string;
  external_api_title: string;
  external_api_url: string | null;
  notes: string | null;
  visited: boolean;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  start_date: string | null;
  completed: boolean;
  places: Place[];
}