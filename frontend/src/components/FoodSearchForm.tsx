"use client";

import { useState, FormEvent } from "react";
import {
  Box,
  Button,
  Heading,
  Input,
  Text,
  VStack,
  HStack,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";

export function FoodSearchForm() {
  const [value, setValue] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!value.trim()) {
      setError("좋아하는 외국 음식 이름을 입력해주세요.");
      return;
    }
    setError("");
    router.push(`/results?food=${encodeURIComponent(value.trim())}`);
  };

  return (
    <Box
      as="form"
      onSubmit={handleSubmit}
      maxW="lg"
      w="100%"
      mx="auto"
      bg="white"
      p={8}
      borderRadius="xl"
      boxShadow="lg"
    >
      <VStack spacing={6} align="stretch">
        <Heading size="lg" textAlign="center">
          어떤 외국 음식을 좋아하시나요?
        </Heading>
        <Text fontSize="sm" color="gray.600" textAlign="center">
          예: Tacos, 타코스, タコス 등 편한 언어로 입력해 주세요.
        </Text>

        <Input
          size="lg"
          placeholder="예: Tacos / 타코스 / タコス"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />

        {error && (
          <Text fontSize="sm" color="red.500">
            {error}
          </Text>
        )}

        <HStack justify="center">
          <Button type="submit" colorScheme="teal" size="lg">
            추천 시작
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
}
