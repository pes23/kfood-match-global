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
      setError("좋아하는 외국 음식 이름을 입력해주세요.\n Please enter the name of a foreign food.");
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
          어떤 음식을 좋아하시나요?
          <br />
          What kind of food do you like?
        </Heading>

        <Text fontSize="sm" color="gray.600" textAlign="center">
          Tacos, 타코스, タコス 등 편한 언어로 입력해 주세요.
          <br />
          Feel free to enter it in any language — Tacos, 타코스, タコス, etc.
        </Text>

        <Input
          size="lg"
          placeholder="Tacos / 타코스 / タコス"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          mt={3}    
          mb={3}
        />

        {error && (
          <Text fontSize="sm" color="red.500">
            {error}
          </Text>
        )}

        <HStack justify="center">
          <Button type="submit" colorScheme="teal" size="lg" textAlign="center">
            추천 시작
            <br />
            Get Recommendations
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
}
