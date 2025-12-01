"use client";

import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Container,
  Heading,
  Spinner,
  Text,
  VStack,
  Alert,
  AlertIcon,
  HStack,
} from "@chakra-ui/react";
import Link from "next/link";
import { RecommendationList } from "@/components/RecommendationList";
import type {
  RecommendationItem,
  RecommendationResponse,
} from "@/types/recommendation";
import { fetchRecommendations } from "@/lib/api";

type Props = {
  searchParams: { food?: string };
};

export default function ResultsContent({ searchParams }: Props) {
  const food = searchParams.food ?? "";
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [items, setItems] = useState<RecommendationItem[]>([]);
  const [inputFood, setInputFood] = useState<string>("");

  useEffect(() => {
    if (!food.trim()) {
      setError("음식 이름이 전달되지 않았습니다. 처음 화면에서 다시 입력해주세요.");
      setLoading(false);
      return;
    }

    let cancelled = false;

    const run = async () => {
      try {
        setLoading(true);
        setError("");

        const res: RecommendationResponse = await fetchRecommendations(food);
        if (cancelled) return;

        setItems(res.items ?? []);
        setInputFood(res.input_food ?? food);
      } catch (e: any) {
        if (cancelled) return;
        setError(e?.message ?? "추천 결과를 가져오는 중 오류가 발생했습니다.");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, [food]);

  return (
    <Container maxW="container.lg" py={16}>
      <VStack spacing={10} align="stretch">
        <Box>
          <Heading size="xl" mb={2}>
            추천 결과 Recommendation Results
            <br />
          </Heading>
          <Text color="gray.600">
            입력한 음식 The food you entered :{" "}
            <Text as="span" fontWeight="bold">
              {food || "알 수 없음"}
            </Text>
          </Text>
        </Box>

        {loading && (
          <VStack spacing={2} align="center">
            <Spinner mt={4} />

            <Text mt={4}>AI가 한국 음식을 찾고 있습니다...</Text>
            <Text>Loading recommendation results...</Text>
          </VStack>
        )}


        {!loading && error && (
          <VStack spacing={4} align="stretch">
            <Alert status="error">
              <AlertIcon />
              {error}
            </Alert>
            <HStack justify="center">
              <Button as={Link} href="/" colorScheme="teal">
                처음으로 돌아가기 \nGo to Home
              </Button>
            </HStack>
          </VStack>
        )}

        {!loading && !error && (
          <>
            {items.length === 0 ? (
              <VStack spacing={4} align="center">
                <Text>조건에 맞는 한국 음식을 찾지 못했습니다. 😢</Text>
                <Button as={Link} href="/" colorScheme="teal">
                  다른 음식으로 다시 시도하기 \nGet recommendations again with another food
                </Button>
              </VStack>
            ) : (
              <Box mt={6} mb={6}>
                <RecommendationList items={items} />
              </Box>
              
            )}

            <HStack justify="center" mt={8}>
              <Button as={Link} href="/" variant="outline" colorScheme="teal" textAlign="center" py={8} px={8} >
                다른 음식으로 다시 추천받기 
                <br />
                Get recommendations again with another food
              </Button>
            </HStack>
          </>
        )}
      </VStack>
    </Container>
  );
}
