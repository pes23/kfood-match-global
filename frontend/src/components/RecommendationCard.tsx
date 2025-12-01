"use client";

import {
  Box,
  Badge,
  Image,
  Text,
  VStack,
  HStack,
  Heading,
} from "@chakra-ui/react";
import type { RecommendationItem } from "@/types/recommendation";
import ChiliLevel from "@/components/ChiliLevel";

type Props = {
  item: RecommendationItem;
};

export function RecommendationCard({ item }: Props) {
  return (
    <Box
      bg="white"
      borderRadius="xl"
      boxShadow="md"
      overflow="hidden"
      w="100%"
      maxW="sm"
    >
      {item.image_url && (
        <Image
          src={item.image_url}
          alt={item.name}
          w="100%"
          h="220px"
          objectFit="cover"
        />
      )}

      <Box p={7}>
        <VStack align="stretch" spacing={5}>
          {/* 음식 이름 */}
          <Heading size="md">{item.name}</Heading>

          {/* 매운 정도 라인 */}
          <HStack spacing={2} align="center">
            <Badge colorScheme="red" variant="subtle">
              매운 정도 Spicy level
            </Badge>

            <ChiliLevel level={item.spicy_level} />
          </HStack>

          {/* 주요 재료 라인 */}
          {item.main_ingredients && (
            <HStack spacing={2} align="center">
              <Badge colorScheme="gray" variant="subtle">
                주요 재료 Main ingredients
              </Badge>

              <Text fontSize="sm" color="gray.700">
                {item.main_ingredients}
              </Text>
            </HStack>
          )}

          {/* 추천 이유 */}
          <Text fontSize="sm" color="gray.800">
            {item.reason}
          </Text>
        </VStack>
      </Box>
    </Box>
  );
}
