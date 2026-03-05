export interface Property {
  id: string;
  lead_id: string;
  property_type: string | null;
  total_units: number | null;
  total_buildings: number | null;
  total_sqft: number | null;
  stories: number | null;
  parking_spaces: number | null;
  permit_number: string | null;
  permit_date: string | null;
  zoning: string | null;
  amenities: string | null;
}
