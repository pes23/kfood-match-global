export type RecommendationItem = {
  name: string;
  spicy_level: number;
  main_ingredients: string;
  reason: string;
  image_url: string;
};

export type RecommendationResponse = {
  input_food: string;
  items: RecommendationItem[];
};
