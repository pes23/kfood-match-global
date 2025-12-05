"use client";

import { SimpleGrid, Text, VStack } from "@chakra-ui/react";
import type { RecommendationItem } from "types/recommendation";
import { RecommendationCard } from "./RecommendationCard";

type Props = {
  items: RecommendationItem[];
};

export function RecommendationList({ items }: Props) {
  if (!items.length) {
    return (
      <Text textAlign="center" color="gray.600">
        아직 추천 결과가 없습니다.
        No recommendations yet.
      </Text>
    );
  }

  // 상위 2개만 보여주기
  const top2 = items.slice(0, 2);

  return (
    <VStack spacing={6} w="100%">
      <SimpleGrid
        columns={{ base: 1, md: 2 }}
        spacing={8}
        w="100%"
        justifyItems="center"
      >
        {top2.map((item, idx) => (
          <RecommendationCard key={idx} item={item} />
        ))}
      </SimpleGrid>
    </VStack>
  );
}
