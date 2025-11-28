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

type Props = {
  item: RecommendationItem;
};

function spicyLabel(level: number) {
  if (level <= 1) return "안 매움";
  if (level === 2) return "약간 매움";
  if (level === 3) return "보통 매움";
  if (level === 4) return "매움";
  return "아주 매움";
}

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

      <Box p={5}>
        <VStack align="stretch" spacing={3}>
          <Heading size="md">{item.name}</Heading>

          <HStack spacing={2}>
            <Badge colorScheme="red">{spicyLabel(item.spicy_level)}</Badge>
            {item.main_ingredients && (
              <Badge colorScheme="gray" variant="subtle">
                주요 재료
              </Badge>
            )}
          </HStack>

          {item.main_ingredients && (
            <Text fontSize="sm" color="gray.700">
              {item.main_ingredients}
            </Text>
          )}

          <Text fontSize="sm" color="gray.800">
            {item.reason}
          </Text>
        </VStack>
      </Box>
    </Box>
  );
}
